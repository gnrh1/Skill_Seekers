#!/bin/bash
# Z.AI GLM-4.6 Model Integration Setup Script
# This script helps you complete the Z.AI model integration

set -e

echo "=================================================="
echo "Z.AI GLM-4.6 Factory Droid Integration"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if config file exists
echo -e "${YELLOW}Step 1: Checking configuration file...${NC}"
if [ -f ~/.factory/config.json ]; then
    echo -e "${GREEN}✓ Configuration file exists at ~/.factory/config.json${NC}"
else
    echo -e "${RED}✗ Configuration file not found!${NC}"
    exit 1
fi

# Step 2: Display current configuration
echo ""
echo -e "${YELLOW}Step 2: Current configuration:${NC}"
cat ~/.factory/config.json
echo ""

# Step 3: Check if API key is set
echo -e "${YELLOW}Step 3: Checking API key status...${NC}"
if grep -q "YOUR_Z_AI_API_KEY_HERE" ~/.factory/config.json; then
    echo -e "${RED}⚠ API key placeholder detected!${NC}"
    echo ""
    echo "You need to add your actual Z.AI API key."
    echo ""
    echo "Options to edit the configuration:"
    echo "  1. nano ~/.factory/config.json"
    echo "  2. code ~/.factory/config.json  (VS Code)"
    echo "  3. open -e ~/.factory/config.json  (TextEdit on macOS)"
    echo ""
    echo "Replace 'YOUR_Z_AI_API_KEY_HERE' with your actual Z.AI API key"
    echo ""
    read -p "Press Enter after you've added your API key..."
else
    echo -e "${GREEN}✓ API key appears to be configured${NC}"
fi

# Step 4: Validate JSON syntax
echo ""
echo -e "${YELLOW}Step 4: Validating JSON syntax...${NC}"
if python3 -m json.tool ~/.factory/config.json > /dev/null 2>&1; then
    echo -e "${GREEN}✓ JSON syntax is valid${NC}"
else
    echo -e "${RED}✗ JSON syntax error detected!${NC}"
    echo "Please fix the JSON syntax in ~/.factory/config.json"
    exit 1
fi

# Step 5: Set secure file permissions
echo ""
echo -e "${YELLOW}Step 5: Setting secure file permissions...${NC}"
chmod 600 ~/.factory/config.json
echo -e "${GREEN}✓ File permissions set to 600 (owner read/write only)${NC}"

# Step 6: Test API endpoint connectivity
echo ""
echo -e "${YELLOW}Step 6: Testing Z.AI API endpoint connectivity...${NC}"
if curl -s -I https://api.z.ai/api/coding/pass/v4 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Z.AI API endpoint is reachable${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify API endpoint (this may be normal if authentication is required)${NC}"
fi

# Step 7: Instructions for next steps
echo ""
echo "=================================================="
echo -e "${GREEN}Configuration Complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps to activate your Z.AI model:"
echo ""
echo "1. Start the Droid CLI:"
echo "   $ droid"
echo ""
echo "2. Inside the Droid CLI, select your model:"
echo "   > /model"
echo ""
echo "3. Look for 'Z.AI GLM-4.6 [Custom]' in the Custom models section"
echo ""
echo "4. Test with a simple prompt:"
echo "   > Write a Python function to reverse a string"
echo ""
echo "5. Check cost tracking (optional):"
echo "   > /cost"
echo ""
echo "=================================================="
echo "Configuration file location: ~/.factory/config.json"
echo "Integration guide: docs/Z_AI_INTEGRATION_GUIDE.md"
echo "=================================================="
