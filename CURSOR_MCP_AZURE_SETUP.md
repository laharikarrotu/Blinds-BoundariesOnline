# Add Azure to MCP Server in Cursor

## ✅ **YES! You can add Azure to your MCP server**

This allows the AI assistant in Cursor to directly interact with your Azure resources (Blob Storage, Computer Vision, etc.).

---

## 🔧 **Step 1: Open MCP Configuration**

1. Open **Cursor**
2. Go to **File → Preferences → Cursor Settings** (or `Cmd+,` on Mac)
3. Click **"Tools & Integrations"** in left sidebar
4. Find **"MCP Tools"** section
5. Click **"New MCP Server"** or edit existing `mcp.json`

---

## 📝 **Step 2: Add Azure MCP Server Configuration**

Add this to your `mcpServers` JSON object:

```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": [
        "-y",
        "@azure/mcp@latest",
        "server",
        "start"
      ],
      "env": {
        "AZURE_STORAGE_ACCOUNT": "blinds-boundaries",
        "AZURE_STORAGE_KEY": "YOUR_STORAGE_KEY_HERE"
      }
    }
  }
}
```

**Replace `YOUR_STORAGE_KEY_HERE`** with your actual storage account key from Azure Portal.

---

## 🔑 **Step 3: Get Your Azure Credentials**

### Option A: Storage Account Key (for Blob Storage)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Storage accounts** → **blinds-boundaries**
3. Click **"Access Keys"** in left menu
4. Copy **"key1"** or **"key2"**
5. Use it in the `AZURE_STORAGE_KEY` environment variable

### Option B: Azure CLI Authentication (Recommended)

Instead of using keys, authenticate with Azure CLI:

```bash
# Install Azure CLI (if not installed)
# Mac: brew install azure-cli
# Or download from: https://aka.ms/installazureclimac

# Login to Azure
az login

# Verify authentication
az account show
```

Then use this configuration (no keys needed):

```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": [
        "-y",
        "@azure/mcp@latest",
        "server",
        "start"
      ]
    }
  }
}
```

---

## 📋 **Step 4: Complete MCP Configuration Example**

Here's a complete example with multiple Azure services:

```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": [
        "-y",
        "@azure/mcp@latest",
        "server",
        "start"
      ],
      "env": {
        "AZURE_STORAGE_ACCOUNT": "blinds-boundaries",
        "AZURE_STORAGE_CONTAINER": "window-images"
      }
    }
  }
}
```

---

## ✅ **Step 5: Restart Cursor**

1. **Save** the MCP configuration
2. **Restart Cursor** completely (quit and reopen)
3. The Azure MCP server will start automatically

---

## 🧪 **Step 6: Test the Integration**

1. Open Cursor's AI chat (`Cmd+L` on Mac, `Ctrl+L` on Windows)
2. Try these prompts:

```
List my Azure storage accounts
```

```
Show me the containers in my blinds-boundaries storage account
```

```
Upload a file to my Azure Blob Storage
```

```
Check my Azure Computer Vision resources
```

---

## 🎯 **What You Can Do with Azure MCP**

Once configured, you can ask the AI to:

- ✅ **List storage accounts** and containers
- ✅ **Upload/download files** to/from Blob Storage
- ✅ **Manage containers** (create, delete, list)
- ✅ **Check Computer Vision** resources
- ✅ **View resource groups** and subscriptions
- ✅ **Monitor Azure services** status
- ✅ **Deploy resources** via MCP commands

---

## 🔒 **Security Notes**

### Option 1: Azure CLI (Recommended)
- ✅ More secure (uses OAuth)
- ✅ No keys in config file
- ✅ Automatic token refresh
- ✅ Better for production

### Option 2: Storage Keys
- ⚠️ Less secure (keys in config)
- ⚠️ Keys don't expire automatically
- ✅ Simpler setup
- ✅ Good for development

**Recommendation**: Use Azure CLI authentication for better security.

---

## 🚨 **Troubleshooting**

### MCP Server Not Starting?
- Check Node.js is installed: `node --version`
- Check npx is available: `npx --version`
- Restart Cursor completely

### Authentication Failed?
- Run `az login` in terminal
- Check `az account show` shows your subscription
- Verify you have permissions to access resources

### Can't Access Storage?
- Verify storage account name: `blinds-boundaries`
- Check container exists: `window-images`
- Verify you have "Storage Blob Data Contributor" role

### MCP Commands Not Working?
- Check Cursor AI chat is using MCP tools
- Look for MCP errors in Cursor's developer console
- Try restarting Cursor

---

## 📚 **Useful MCP Commands**

Once set up, you can use natural language:

```
"List all files in my window-images container"
```

```
"Upload this image to Azure Blob Storage"
```

```
"Create a new container called 'test-images'"
```

```
"Show me my Azure Computer Vision endpoints"
```

```
"Check the status of my Azure resources"
```

---

## ✅ **Success Checklist**

- [ ] MCP configuration added to Cursor
- [ ] Azure CLI installed and authenticated (`az login`)
- [ ] Cursor restarted
- [ ] Test command works: "List my Azure storage accounts"
- [ ] Can access Blob Storage via MCP

---

**Once configured, the AI in Cursor can directly manage your Azure resources!** 🚀

