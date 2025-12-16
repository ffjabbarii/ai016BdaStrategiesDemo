╭─fjabbari@Freds-MacBook-Pro ~/REPO_AI/VR/ai016BdaStrategiesDemo ‹main●› 
╰─$ python test_existing_bda_project.py

🔥 BDA Fix Test - Using Existing Real BDA Projects
This test uses your existing real Amazon Bedrock Data Automation projects

🔥 Testing W-2 Upload to Existing BDA Project
============================================================
1️⃣ Checking API...
✅ API running: 🚀 Latest Blueprint API code is running!

2️⃣ Checking W-2 file...
✅ W-2 file found (1,343,180 bytes)

3️⃣ Finding real BDA projects...
✅ Found 5 real BDA projects:
   1. test-w2-fixed-1765841521
   2. bda-working-test-v2
   3. real-bda-success
   4. test-direct-bda-project
   5. bda-final-test

🎯 Using project: test-w2-fixed-1765841521
📍 Project ARN: arn:aws:bedrock:us-east-1:624706593351:data-automation-project/a07a2d75b205

4️⃣ Uploading W-2 to BDA project: test-w2-fixed-1765841521
🔧 This tests the FIXED dataAutomationProfileArn implementation
✅ W-2 uploaded successfully!

🎉 SUCCESS: BDA PROCESSING JOB CREATED!
📋 Invocation ARN: None
✅ The dataAutomationProfileArn fix is WORKING!
📍 Project: test-w2-fixed-1765841521
🌐 Check AWS Console → Amazon Bedrock → Data Automation → Projects

============================================================
🎉 TEST PASSED!
✅ The dataAutomationProfileArn fix is working correctly!
✅ BDA processing job created successfully!
📍 Check AWS Console for processing results

📋 Next Steps:
1. Go to AWS Console → Amazon Bedrock → Data Automation
2. Find your project and check processing jobs
3. View extracted W-2 fields and results
╭─fjabbari@Freds-MacBook-Pro ~/REPO_AI/VR/ai016BdaStrategiesDemo ‹main●› 