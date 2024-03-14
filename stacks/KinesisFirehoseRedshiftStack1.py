import os

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_kinesis as kinesis
import aws_cdk.aws_logs as logs
import aws_cdk.aws_redshift as redshift
import aws_cdk.aws_s3 as s3
from constructs import Construct
from dotenv import load_dotenv

load_dotenv()


redshift_master_user = os.environ.get("REDSHIFT_MASTER_USER")
redshift_master_password = os.environ.get("REDSHIFT_MASTER_PW")
redshift_db_name = os.environ.get("REDSHIFT_DB_NAME")
redshift_cluster_name = os.environ.get("REDSHIFT_CLUSTER_NAME")
s3_bucket_name = os.environ.get("S3_BUCKET_NAME")

table_name = os.environ.get("TABLE_NAME")


class KinesisFirehoseRedshiftStack1(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create kinesis stream
        self.kinesis_stream = kinesis.Stream(
            self,
            "KinesisStream",
            stream_name="kinesis-stream",
            shard_count=1,
            stream_mode=kinesis.StreamMode("PROVISIONED"),
        )

        # Firehose Kinesis access role
        self.role_firehose_kinesis = iam.Role(
            self,
            "FirehoseKinesisRole",
            role_name="firehose-kinesis-role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
        )
        policy_firehose_kinesis = iam.Policy(
            self,
            "FirehoseKinesisPolicy",
            policy_name="firehose-kinesis-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "kinesis:DescribeStream",
                        "kinesis:GetShardIterator",
                        "kinesis:GetRecords",
                        "kinesis:ListShards",
                    ],
                    resources=[self.kinesis_stream.stream_arn],
                ),
            ],
        )
        self.role_firehose_kinesis.attach_inline_policy(policy_firehose_kinesis)

        # S3 bucket for redshift intermediate storage
        self.bucket = s3.Bucket(
            self,
            "S3Bucket",
            bucket_name=s3_bucket_name,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # required since default value is RETAIN
            # auto_delete_objects=True,  # required to delete the not empty bucket
            # auto_delete requires lambda therefore not yet supported by Localstack
        )

        # cloud watch logging group and stream for firehose s3 error logging
        self.firehose_s3_log_group_name = "firehose-s3-log-group"
        firehose_s3_log_group = logs.LogGroup(
            self,
            "FirehoseLogGroup",
            log_group_name=self.firehose_s3_log_group_name,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # required since default value is RETAIN
        )
        # create log stream
        self.firehose_s3_log_stream_name = "firehose-s3-log-stream"
        firehose_s3_log_group.add_stream(
            "FirehoseLogStream", log_stream_name=self.firehose_s3_log_stream_name
        )

        # firehose s3 access role
        self.role_firehose_s3 = iam.Role(
            self,
            "FirehoseS3Role",
            role_name="firehose-s3-role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
        )
        policy_firehose_s3 = iam.Policy(
            self,
            "FirehoseS3Policy",
            policy_name="firehose-s3-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:PutObject",
                    ],
                    resources=[self.bucket.bucket_arn, f"{self.bucket.bucket_arn}/*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["logs:PutLogEvents", "logs:CreateLogStream"],
                    resources=[firehose_s3_log_group.log_group_arn],
                ),
            ],
        )
        self.role_firehose_s3.attach_inline_policy(policy_firehose_s3)

        # Create Redshift cluster VPC
        self.redshift_vpc = ec2.Vpc(
            self,
            "RedshiftVpc",
            vpc_name="redshift-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.10.0.0/16"),  # cidr="10.10.0.0.0/16"
            max_azs=1,
            nat_gateways=1,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", cidr_mask=24, subnet_type=ec2.SubnetType.PUBLIC
                ),
            ],
        )

        redshift_vpc_subnet_ids = self.redshift_vpc.select_subnets(
            subnet_type=ec2.SubnetType.PUBLIC
        ).subnet_ids

        # crete security group to allow inbound traffic to redshift cluster
        redshift_security_group = ec2.SecurityGroup(
            self,
            "RedshiftSecurityGroup",
            vpc=self.redshift_vpc,
            security_group_name="redshift-security-group",
            description="Security group for redshift cluster",
            allow_all_outbound=True,
        )
        redshift_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(5439),  # allow redshift port
        )
        redshift_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),  # allow ssh,
        )

        # Create Redshift S3 access role
        role_redshift_cluster = iam.Role(
            self,
            "RedshiftClusterRole",
            role_name="redshift-cluster-role",
            assumed_by=iam.ServicePrincipal("redshift.amazonaws.com"),
            # alternatively use the following to attach managed policies
            # managed_policies=[
            #     iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            # ],
        )

        policy_redshift_cluster = iam.Policy(
            self,
            "RedshiftPolicy",
            policy_name="redshift-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                    ],
                    resources=[self.bucket.bucket_arn, f"{self.bucket.bucket_arn}/*"],
                ),
            ],
        )
        role_redshift_cluster.attach_inline_policy(policy_redshift_cluster)

        # create subnet group for cluster
        redshift_cluster_subnet_group = redshift.CfnClusterSubnetGroup(
            self,
            "RedshiftClusterSubnetGroup",
            subnet_ids=redshift_vpc_subnet_ids,
            description="Redshift Cluster Subnet Group",
        )

        # create redshift cluster
        ec2_instance_type = "dc2.large"
        self.redshift_cluster = redshift.CfnCluster(
            self,
            "RedshiftCluster",
            cluster_identifier=redshift_cluster_name,
            cluster_type="single-node",
            number_of_nodes=1,
            db_name=redshift_db_name,
            master_username=redshift_master_user,
            master_user_password=redshift_master_password,
            iam_roles=[role_redshift_cluster.role_arn],
            node_type=f"{ec2_instance_type}",
            cluster_subnet_group_name=redshift_cluster_subnet_group.ref,
            vpc_security_group_ids=[redshift_security_group.security_group_id],
            publicly_accessible=True,
        )

        # specify resource outputs
        cdk.CfnOutput(self, "KinesisStreamName", value=self.kinesis_stream.stream_name)
        redshift_cluster_port = self.redshift_cluster.get_att(
            "Endpoint.Port"
        ).to_string()
        redshift_cluster_address = self.redshift_cluster.get_att(
            "Endpoint.Address"
        ).to_string()
        cdk.CfnOutput(self, "BucketName", value=self.bucket.bucket_name)
        cdk.CfnOutput(
            self, "RedshiftClusterName", value=self.redshift_cluster.cluster_identifier
        )
        cdk.CfnOutput(
            self, "RedshiftClusterAddress", value=redshift_cluster_address
        )  # redshift_cluster.attr_endpoint_address)
        cdk.CfnOutput(
            self, "RedshiftClusterPort", value=redshift_cluster_port
        )  # redshift_cluster.attr_endpoint_port)
