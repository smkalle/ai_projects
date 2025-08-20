# Hands-On Tutorial: Building and Using DevGenius - An AI-Powered AWS Solution Generator


## Introduction

DevGenius is an innovative AI-powered application from AWS Samples that transforms natural language project ideas into complete, deployable AWS solutions. It leverages Amazon Bedrock and Anthropic's Claude models to provide architecture diagrams, cost estimates, infrastructure as code, and comprehensive technical documentation. This tool represents a significant advancement in conversational AI for DevOps, similar to how Google's Duet AI assists with code generation but specifically tailored for AWS infrastructure.

This comprehensive, hands-on tutorial will guide you through setting up, deploying, and using DevGenius from scratch. We'll cover local development, Docker containerization, and full AWS deployment using CDK. By the end, you'll be able to generate complete AWS solutions from simple ideas like "Build a data lake for analytics" and deploy them with a single command.

**Time Estimate**: 2-3 hours for complete setup  
**Skill Level**: Intermediate (assumes basic AWS and Python knowledge)

## What is DevGenius?

DevGenius is an open-source AI application that demonstrates the power of conversational AI for infrastructure design. Key capabilities include:

- **Conversational Design**: Interactive chat interface for iteratively building and refining AWS architectures
- **Multi-format Outputs**: Generates architecture diagrams (draw.io format), Infrastructure as Code (CDK/CloudFormation), cost estimates, and detailed documentation
- **Image Analysis**: Upload sketches or whiteboard drawings for AI analysis and conversion to deployable solutions
- **Knowledge-Driven**: Powered by Amazon Bedrock with Claude models and a comprehensive AWS documentation knowledge base

### Architecture Overview

The system consists of several key components working together:

1. **Frontend**: Streamlit web application providing the user interface
2. **AI Engine**: Amazon Bedrock with Claude models for conversational AI
3. **Knowledge Base**: AWS documentation embedded in OpenSearch for accurate recommendations
4. **Storage**: S3 for artifacts, DynamoDB for sessions, OpenSearch for embeddings
5. **Infrastructure**: ECS Fargate for hosting, CloudFront for distribution, Cognito for authentication

## Prerequisites

Before starting, ensure you have:

### Required Software
- **AWS Account**: With administrator permissions or at least permissions for Bedrock, S3, DynamoDB, OpenSearch, ECS, CloudFront, ALB, Cognito, and CDK
- **AWS CLI**: Installed and configured (`aws configure`)
- **Python 3.12+**: Download from python.org
- **Node.js 18+**: For AWS CDK (npm install -g aws-cdk)
- **Docker**: For containerized deployment
- **Git**: For cloning the repository

### AWS Setup
1. **Verify AWS CLI Configuration**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Enable Bedrock Models**: 
   - Navigate to AWS Console > Amazon Bedrock > Model access
   - Request access to Anthropic Claude models (Claude-3-Sonnet recommended)

3. **Set Default Region**:
   ```bash
   aws configure set region us-west-2  # Recommended for Bedrock availability
   ```

### Cost Considerations
- Amazon Bedrock charges per API call (~$0.003 per 1K tokens)
- ECS Fargate, OpenSearch, and other services incur ongoing costs
- Estimate: $5-20/month for development usage
- Use AWS Cost Explorer to monitor expenses

## Step 1: Repository Setup and Exploration

### Clone the DevGenius Repository

```bash
# Clone the repository
git clone https://github.com/aws-samples/sample-devgenius-aws-solution-builder.git
cd sample-devgenius-aws-solution-builder

# Explore the structure
tree -L 2  # or use `ls -la` on Windows
```

### Understanding the Project Structure

```
sample-devgenius-aws-solution-builder/
â”œâ”€â”€ README.md                    # Project documentation
â”œâ”€â”€ app.py                      # CDK application entry point  
â”œâ”€â”€ requirements.txt            # Python dependencies
â”œâ”€â”€ cdk.json                    # CDK configuration
â”œâ”€â”€ package.json                # Node.js dependencies for CDK
â”œâ”€â”€ chatbot/                    # Streamlit application
â”‚   â”œâ”€â”€ app.py                 # Main Streamlit app
â”‚   â”œâ”€â”€ agent.py               # Bedrock agent integration
â”‚   â”œâ”€â”€ requirements.txt       # Python dependencies
â”‚   â””â”€â”€ Dockerfile            # Container definition
â”œâ”€â”€ lib/                       # CDK infrastructure stacks
â”‚   â”œâ”€â”€ devgenius-stack.ts    # Main CDK stack
â”‚   â””â”€â”€ constructs/           # Reusable CDK constructs
â””â”€â”€ docs/                     # Documentation and examples
```

## Step 2: Local Environment Setup

### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv devgenius-env
source devgenius-env/bin/activate  # Windows: devgenius-env\Scripts\activate

# Install CDK dependencies
npm install

# Install Python dependencies for the chatbot
cd chatbot
pip install -r requirements.txt
cd ..
```

### Install AWS CDK

```bash
# Install CDK CLI globally
npm install -g aws-cdk

# Verify installation
cdk --version

# Bootstrap CDK (one-time setup per region/account)
cdk bootstrap
```

## Step 3: Infrastructure Deployment with CDK

### Review the CDK Stack

Before deploying, let's understand what will be created:

```bash
# Generate CloudFormation template for review
cdk synth
```

This creates:
- **Amazon Bedrock Agent**: Conversational AI with Claude models
- **Knowledge Base**: AWS documentation embedded in OpenSearch
- **OpenSearch Serverless**: Vector database for embeddings
- **DynamoDB Tables**: For conversation history and feedback
- **S3 Bucket**: For storing generated artifacts
- **ECS Fargate Cluster**: For hosting the Streamlit app
- **CloudFront Distribution**: For global content delivery
- **Application Load Balancer**: For traffic distribution
- **Amazon Cognito**: For user authentication

### Deploy the Infrastructure

```bash
# Deploy all resources
cdk deploy --all

# Alternative: Deploy with approval for all changes
cdk deploy --all --require-approval never
```

**Expected Output**: The deployment takes 15-25 minutes. You'll see:
```
DevGenius-Stack: deploying...
DevGenius-Stack: creating CloudFormation stack...
âœ… DevGenius-Stack

Outputs:
DevGenius-Stack.BedrockAgentId = ABCDEF123456
DevGenius-Stack.BedrockAgentAliasId = 7890GHIJKL
DevGenius-Stack.S3BucketName = devgenius-artifacts-bucket-xyz
DevGenius-Stack.ConversationTableName = DevGenius-ConversationTable
DevGenius-Stack.FeedbackTableName = DevGenius-FeedbackTable
DevGenius-Stack.SessionTableName = DevGenius-SessionTable
DevGenius-Stack.StreamlitAppURL = https://d123456789.cloudfront.net
```

**Important**: Save these outputs! You'll need them for configuration.

### Post-Deployment Verification

```bash
# Verify Bedrock agent creation
aws bedrock-agent list-agents --region us-west-2

# Check knowledge base status
aws bedrock-agent list-knowledge-bases --region us-west-2

# Verify OpenSearch collection
aws opensearchserverless list-collections --region us-west-2
```

## Step 4: Environment Configuration

### Set Environment Variables

Using the CDK outputs from Step 3, configure your environment:

```bash
# For Linux/macOS
export AWS_REGION="us-west-2"
export BEDROCK_AGENT_ID="ABCDEF123456"  # Replace with your output
export BEDROCK_AGENT_ALIAS_ID="7890GHIJKL"  # Replace with your output
export S3_BUCKET_NAME="devgenius-artifacts-bucket-xyz"  # Replace with your output
export CONVERSATION_TABLE_NAME="DevGenius-ConversationTable"
export FEEDBACK_TABLE_NAME="DevGenius-FeedbackTable"
export SESSION_TABLE_NAME="DevGenius-SessionTable"

# For Windows PowerShell
$env:AWS_REGION="us-west-2"
$env:BEDROCK_AGENT_ID="ABCDEF123456"
# ... (repeat for all variables)
```

### Create Environment File (Optional)

For persistence, create a `.env` file in the `chatbot/` directory:

```bash
cd chatbot
cat > .env << EOF
AWS_REGION=us-west-2
BEDROCK_AGENT_ID=ABCDEF123456
BEDROCK_AGENT_ALIAS_ID=7890GHIJKL
S3_BUCKET_NAME=devgenius-artifacts-bucket-xyz
CONVERSATION_TABLE_NAME=DevGenius-ConversationTable
FEEDBACK_TABLE_NAME=DevGenius-FeedbackTable
SESSION_TABLE_NAME=DevGenius-SessionTable
EOF
```

## Step 5: Running Locally with Streamlit

### Start the Application

```bash
cd chatbot
streamlit run app.py
```

**Expected Output**:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```

### Initial Setup Verification

1. **Open Browser**: Navigate to http://localhost:8501
2. **Check Connection**: The app should load without errors
3. **Test Basic Functionality**: Try entering a simple query like "Hello"

### Troubleshooting Common Issues

**Issue**: `ModuleNotFoundError: No module named 'boto3'`
```bash
pip install boto3 streamlit anthropic
```

**Issue**: `CredentialsError: Unable to locate credentials`
```bash
aws configure
# Enter your AWS credentials
```

**Issue**: `BedrockAgentNotFound`
- Verify the agent ID is correct from CDK outputs
- Ensure the agent status is "PREPARED" in the AWS console

## Step 6: Using DevGenius - Hands-On Examples

### Example 1: Building a Data Lake Architecture

1. **Start Conversation**: In the Streamlit interface, enter:
   ```
   I want to build a data lake in AWS for storing and analyzing customer data from multiple sources including databases, log files, and real-time streams.
   ```

2. **Review Initial Response**: The AI will suggest an architecture with:
   - Amazon S3 for data lake storage
   - AWS Glue for ETL processing
   - Amazon Athena for querying
   - AWS Kinesis for streaming data
   - Amazon QuickSight for visualization

3. **Iterate and Refine**: Add requirements:
   ```
   Add security features including encryption at rest and in transit, and implement data governance with AWS Lake Formation.
   ```

4. **Generate Outputs**:
   - Click "Generate Architecture Diagram" â†’ Downloads a draw.io file
   - Click "Generate CDK Code" â†’ Provides TypeScript CDK code
   - Click "Generate Cost Estimate" â†’ Shows monthly cost breakdown
   - Click "Generate Documentation" â†’ Creates comprehensive guide

### Example 2: Microservices Architecture

```
Design a microservices architecture on AWS with:
- API Gateway for routing
- Lambda functions for business logic  
- DynamoDB for data storage
- SQS for messaging
- CloudWatch for monitoring
- Implement CI/CD pipeline with CodePipeline
```

### Example 3: Image Upload Analysis

1. **Create Architecture Sketch**: Draw a simple AWS architecture on whiteboard/paper
2. **Take Photo**: Save as JPG/PNG
3. **Upload**: Use the file upload feature in Streamlit
4. **AI Analysis**: DevGenius will analyze and explain your architecture
5. **Enhancement**: Ask for improvements or code generation

## Step 7: Docker Deployment

### Build Docker Image

```bash
cd chatbot

# Build the image
docker build -t devgenius-app .

# Verify image creation
docker images | grep devgenius-app
```

### Run with Docker

```bash
# Run container with environment variables
docker run -p 8501:8501 \
  -e AWS_REGION="us-west-2" \
  -e BEDROCK_AGENT_ID="ABCDEF123456" \
  -e BEDROCK_AGENT_ALIAS_ID="7890GHIJKL" \
  -e S3_BUCKET_NAME="devgenius-artifacts-bucket-xyz" \
  -e CONVERSATION_TABLE_NAME="DevGenius-ConversationTable" \
  -e FEEDBACK_TABLE_NAME="DevGenius-FeedbackTable" \
  -e SESSION_TABLE_NAME="DevGenius-SessionTable" \
  devgenius-app
```

### Access Dockerized Application

Open http://localhost:8501 - the application should function identically to the local setup.

## Step 8: Production Deployment Access

### Access the Deployed Application

1. **Get Application URL**: Use the CloudFront URL from CDK outputs
2. **Create Cognito User**:
   ```bash
   # Get User Pool ID from AWS Console
   aws cognito-idp admin-create-user \
     --user-pool-id us-west-2_XXXXXXXXX \
     --username your-email@example.com \
     --user-attributes Name=email,Value=your-email@example.com \
     --temporary-password TempPass123! \
     --message-action SUPPRESS
   ```

3. **Login**: Access the CloudFront URL and login with your credentials

### Configure Custom Domain (Optional)

```bash
# Add to your CDK stack for custom domain
# This requires Route 53 hosted zone and ACM certificate
```

## Step 9: Advanced Features and Customization

### Customizing the Knowledge Base

```bash
# Add custom documents to the knowledge base
aws s3 cp your-custom-docs.pdf s3://your-knowledge-base-bucket/documents/
```

### Modifying Prompts

Edit the system prompts in the CDK stack to customize AI behavior:

```typescript
// In lib/devgenius-stack.ts
const instruction = `
You are an expert AWS Solutions Architect specialized in [YOUR DOMAIN].
Focus on [YOUR SPECIFIC REQUIREMENTS].
`;
```

### Extending with Custom Tools

Add custom functions to the Bedrock agent for specific use cases:

```python
# In chatbot/agent.py
def custom_analysis_tool(architecture_type):
    # Your custom logic here
    return analysis_result
```

## Step 10: Monitoring and Maintenance

### CloudWatch Monitoring

```bash
# View application logs
aws logs describe-log-groups --log-group-name-prefix="/aws/ecs/devgenius"

# Monitor Bedrock usage
aws logs describe-log-groups --log-group-name-prefix="/aws/bedrock"
```

### Cost Optimization

1. **Monitor Usage**: Use AWS Cost Explorer to track expenses
2. **Right-size Resources**: Adjust ECS task definitions based on usage
3. **Optimize Bedrock Calls**: Implement caching for repeated queries

### Performance Tuning

```bash
# Scale ECS service
aws ecs update-service \
  --cluster devgenius-cluster \
  --service devgenius-service \
  --desired-count 2
```

## Step 11: Cleanup and Resource Management

### Destroying Resources

When you're done experimenting:

```bash
# Destroy all CDK resources
cdk destroy --all

# Confirm deletion when prompted
# This removes all AWS resources and stops billing
```

### Selective Resource Cleanup

```bash
# Destroy only specific stacks
cdk destroy DevGenius-Stack
```

### Manual Cleanup (if needed)

Some resources might require manual deletion:

```bash
# Empty and delete S3 buckets
aws s3 rm s3://your-bucket-name --recursive
aws s3 rb s3://your-bucket-name

# Delete Cognito user pool (if not destroyed by CDK)
aws cognito-idp delete-user-pool --user-pool-id your-pool-id
```

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: CDK deployment fails with permission errors
```bash
# Ensure IAM permissions
aws iam get-user
# Verify AdministratorAccess or specific permissions
```

**Issue**: Bedrock agent preparation fails
```bash
# Check model access
aws bedrock list-foundation-models --region us-west-2
# Ensure Claude models are enabled
```

**Issue**: OpenSearch collection creation timeout
```bash
# Check service quotas
aws service-quotas get-service-quota \
  --service-code aoss \
  --quota-code L-D7DA27C5
```

**Issue**: High costs
```bash
# Set up billing alerts
aws budgets create-budget --account-id YOUR-ACCOUNT-ID --budget file://budget.json
```

### Performance Issues

1. **Slow Response Times**: Increase ECS task CPU/memory
2. **Knowledge Base Queries**: Optimize OpenSearch index settings
3. **Bedrock Throttling**: Implement exponential backoff

### Security Best Practices

```bash
# Enable CloudTrail for audit logging
aws cloudtrail create-trail --name devgenius-trail --s3-bucket-name your-logging-bucket

# Enable GuardDuty for threat detection
aws guardduty create-detector --enable
```

## Advanced Extensions

### Integration with GitHub

Connect DevGenius to automatically create GitHub repositories with generated code:

```python
# Add to chatbot/agent.py
import github
def create_github_repo(name, code):
    g = github.Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_user().create_repo(name)
    repo.create_file("main.py", "Initial commit", code)
    return repo.html_url
```

### Multi-Cloud Support

Extend DevGenius to generate code for other cloud providers:

```python
# Add cloud provider selection
cloud_provider = st.selectbox("Choose Cloud Provider", ["AWS", "GCP", "Azure"])
if cloud_provider == "GCP":
    # Add GCP-specific logic
```

### Custom Deployment Pipelines

```bash
# Add CodePipeline for automated deployments
# This would be added to the CDK stack
```

## Best Practices and Tips

### Development Workflow

1. **Version Control**: Always commit CDK changes before deployment
2. **Environment Separation**: Use separate AWS accounts for dev/staging/prod
3. **Infrastructure Testing**: Use CDK assertions for unit testing
4. **Cost Management**: Implement resource tagging for cost allocation

### Security Considerations

1. **Least Privilege**: Use minimal IAM permissions
2. **Encryption**: Enable encryption for all data stores
3. **Network Security**: Use VPC endpoints where possible
4. **Access Control**: Implement proper Cognito user management

### Performance Optimization

1. **Caching**: Implement Redis for frequently accessed data
2. **CDN Usage**: Leverage CloudFront for static assets
3. **Database Optimization**: Use DynamoDB efficiently with proper keys
4. **Model Selection**: Choose appropriate Bedrock models for cost/performance

## AI Engineer Insights

### Comparison with Google Cloud AI

From my experience with Google Cloud's AI Platform:

1. **Model Access**: Similar to Vertex AI's model garden, Bedrock provides managed access to foundation models
2. **Knowledge Integration**: Comparable to Google's Enterprise Search for document retrieval
3. **Scaling**: Both platforms offer similar serverless scaling capabilities
4. **Cost Management**: AWS and GCP have comparable pricing models for AI services

### Technical Deep Dive

**Bedrock Agent Architecture**: The agent uses a sophisticated orchestration layer that:
- Parses user intent using Claude's natural language understanding
- Retrieves relevant information from the knowledge base using vector similarity
- Generates responses using retrieval-augmented generation (RAG)
- Maintains conversation context across multiple turns

**Vector Search Implementation**: OpenSearch Serverless provides:
- Automatic scaling based on query volume
- Built-in vector similarity search using cosine similarity
- Integration with Bedrock embeddings for semantic search

## Conclusion

You've now successfully built, deployed, and used DevGenius - an AI-powered AWS solution generator! This tutorial demonstrated:

- **Infrastructure as Code**: Using AWS CDK for reproducible deployments
- **Conversational AI**: Leveraging Amazon Bedrock and Claude models
- **Full-Stack Development**: From frontend (Streamlit) to backend (AWS services)
- **Production Deployment**: Container orchestration with ECS Fargate
- **Cost Management**: Monitoring and optimization strategies

### Next Steps

1. **Experiment**: Try complex architecture requests to see AI capabilities
2. **Customize**: Modify prompts and add domain-specific knowledge
3. **Integrate**: Connect with your existing AWS accounts and workflows
4. **Contribute**: Consider contributing improvements to the open-source project
5. **Scale**: Implement the patterns in your organization's infrastructure

### Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [CDK Developer Guide](https://docs.aws.amazon.com/cdk/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [DevGenius GitHub Repository](https://github.com/aws-samples/sample-devgenius-aws-solution-builder)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)

This hands-on experience with DevGenius provides a solid foundation for building AI-powered infrastructure tools and understanding the intersection of generative AI with cloud computing. The patterns demonstrated here are applicable to many other AI-driven automation projects in the cloud.

---

**About the Author**: This tutorial was written from the perspective of a Google SDE3 AI Engineer with extensive experience in cloud AI platforms, infrastructure automation, and large-scale distributed systems. The insights provided draw from practical experience with both Google Cloud and AWS AI services.
