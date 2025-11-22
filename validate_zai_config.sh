#!/bin/bash
# Z.AI GLM-4.6 Model Integration Validation Script (Non-Interactive)
# This script validates your Z.AI model configuration

set -e

echo "=================================================="
echo "Z.AI GLM-4.6 Factory Droid Integration Validation"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check if config file exists
echo -e "${BLUE}[Step 1/6]${NC} Checking configuration file..."
if [ -f ~/.factory/config.json ]; then
    echo -e "${GREEN}✓ Configuration file exists at ~/.factory/config.json${NC}"
else
    echo -e "${RED}✗ Configuration file not found!${NC}"
    exit 1
fi

# Step 2: Display current configuration
echo ""
echo -e "${BLUE}[Step 2/6]${NC} Current configuration:"
echo "-------------------------------------------"
cat ~/.factory/config.json
echo "-------------------------------------------"

# Step 3: Check if API key is set
echo ""
echo -e "${BLUE}[Step 3/6]${NC} Checking API key status..."
if grep -q "YOUR_Z_AI_API_KEY_HERE" ~/.factory/config.json; then
    echo -e "${YELLOW}⚠ API key placeholder detected!${NC}"
    echo ""
    echo "ACTION REQUIRED: Add your actual Z.AI API key"
    echo ""
    echo "Edit the file with one of these commands:"
    echo "  nano ~/.factory/config.json"
    echo "  code ~/.factory/config.json"
    echo "  open -e ~/.factory/config.json"
    echo ""
    echo "Replace 'YOUR_Z_AI_API_KEY_HERE' with your actual key"
    API_KEY_STATUS="MISSING"
else
    echo -e "${GREEN}✓ API key appears to be configured${NC}"
    API_KEY_STATUS="CONFIGURED"
fi

# Step 4: Validate JSON syntax
echo ""
echo -e "${BLUE}[Step 4/6]${NC} Validating JSON syntax..."
if python3 -m json.tool ~/.factory/config.json > /dev/null 2>&1; then
    echo -e "${GREEN}✓ JSON syntax is valid${NC}"
else
    echo -e "${RED}✗ JSON syntax error detected!${NC}"
    echo "Please fix the JSON syntax in ~/.factory/config.json"
    exit 1
fi

# Step 5: Set secure file permissions
echo ""
echo -e "${BLUE}[Step 5/6]${NC} Setting secure file permissions..."
chmod 600 ~/.factory/config.json
echo -e "${GREEN}✓ File permissions set to 600 (owner read/write only)${NC}"

# Step 6: Test API endpoint connectivity
echo ""
echo -e "${BLUE}[Step 6/6]${NC} Testing Z.AI API endpoint connectivity..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://api.z.ai/api/coding/pass/v4 2>/dev/null || echo "000")
if [ "$HTTP_STATUS" != "000" ]; then
    echo -e "${GREEN}✓ Z.AI API endpoint is reachable (HTTP $HTTP_STATUS)${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify API endpoint (may require authentication)${NC}"
fi

# Summary
echo ""
echo "=================================================="
echo "VALIDATION SUMMARY"
echo "=================================================="
echo ""
echo -e "Configuration File: ${GREEN}✓ Valid${NC}"
echo -e "JSON Syntax:        ${GREEN}✓ Valid${NC}"
echo -e "File Permissions:   ${GREEN}✓ Secure (600)${NC}"

if [ "$API_KEY_STATUS" = "MISSING" ]; then
    echo -e "API Key:            ${RED}✗ PLACEHOLDER - ACTION REQUIRED${NC}"
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  NEXT STEP: Add your Z.AI API key to the config   ${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo "1. Edit: nano ~/.factory/config.json"
    echo "2. Replace: YOUR_Z_AI_API_KEY_HERE → your-actual-key"
    echo "3. Save and run this script again to verify"
else
    echo -e "API Key:            ${GREEN}✓ Configured${NC}"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  READY! Activate your model in Droid CLI          ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo "1. Start Droid CLI:  droid"
    echo "2. Select model:     /model"
    echo "3. Look for:         Z.AI GLM-4.6 [Custom]"
    echo "4. Test it:          Write a Python hello world function"
fi

echo ""
echo "=================================================="
echo "Configuration: ~/.factory/config.json"
echo "Documentation: docs/Z_AI_INTEGRATION_GUIDE.md"
echo "=================================================="
