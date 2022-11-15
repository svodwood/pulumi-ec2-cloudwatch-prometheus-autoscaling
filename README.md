# EC2 Autoscaling and Prometheus Exporters
A demo Pulumi project to set up EC2 autoscaling policies based on Prometheus exporters metrics

[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new?template=https://github.com/svodwood/pulumi-ec2-cloudwatch-prometheus-autoscaling)

## Abstract

Quite a few workloads may still require deployment to virtual machines instead of container orchestration platforms, yet still, have to be intelligently autoscaled. For example, a compound workload running on a stateless EC2 instance in an EC2 Autoscaling Group may emit various Prometheus-compatible metrics via Prometheus exporters. A simplified model for such a use case could be an Amazon Linux 2 instance running a node-exporter, exposing OS metrics, and a workload application delivering its own set of Prometheus-compatible metrics.

This project illustrates how to configure an EC2 Autoscaling Group to use these metrics within Target Tracking Scaling Policies with the help of the AWS Cloudwatch agent.

## High-level Flow
EC2 instance -> locahost Prometheus exporter -> localhost Cloudwatch agent -> Cloudwatch log stream/metrics/alarms -> EC2 target tracking scaling policy

## Implementation Guide
[Link to detailed guide](https://svodwood.github.io/devops-pastebin/ec2-autoscaling-groups-prometheus-metrics/)
