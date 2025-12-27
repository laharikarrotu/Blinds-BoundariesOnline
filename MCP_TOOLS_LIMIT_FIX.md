# Fix: Exceeding Total Tools Limit (104 tools)

## 🚨 **Problem**
Cursor has a limit on the total number of MCP tools that can be active. You currently have **104 tools** from your enabled servers, which exceeds the limit.

---

## 🔧 **Solution: Disable Unused MCP Servers**

### **Option 1: Comment Out Servers You Don't Need**

Edit `/Users/laharikarrotu/.cursor/mcp.json` and comment out servers you're not actively using:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    },
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=yphayjbfwxppmvxblbtr",
      "headers": {}
    },
    "vercel": {
      "url": "https://mcp.vercel.com"
    }
    // Temporarily disabled to reduce tool count
    // "railway": {
    //   "command": "npx",
    //   "args": [
    //     "-y",
    //     "@railway/mcp-server"
    //   ],
    //   "env": {
    //     "PATH": "/Users/laharikarrotu/.npm-global/bin:${PATH}"
    //   }
    // },
    // "azure": {
    //   "command": "npx",
    //   "args": [
    //     "-y",
    //     "@azure/mcp@latest",
    //     "server",
    //     "start"
    //   ]
    // }
  }
}
```

### **Option 2: Remove Servers Completely**

If you don't need certain servers, remove them entirely:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    },
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=yphayjbfwxppmvxblbtr",
      "headers": {}
    }
  }
}
```

---

## 📊 **Tool Count by Server** (Typical)

- **GitHub MCP**: ~20-30 tools
- **Supabase MCP**: ~15-25 tools
- **Vercel MCP**: ~20-30 tools
- **Railway MCP**: ~15-20 tools
- **Azure MCP**: ~20-30 tools

**Total**: ~90-135 tools (varies by server versions)

---

## 🎯 **Recommended Configuration**

### **For Your Project (Blinds & Boundaries):**

Keep only what you need:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    },
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

**Why:**
- ✅ **GitHub**: For code management, PRs, issues
- ✅ **Azure**: For your Azure Blob Storage, Computer Vision
- ❌ **Supabase**: Not using in this project
- ❌ **Vercel**: Can enable when deploying frontend
- ❌ **Railway**: Not using in this project

---

## 🔄 **How to Enable/Disable Servers**

### **Disable a Server:**
1. Open `/Users/laharikarrotu/.cursor/mcp.json`
2. Remove or comment out the server entry
3. Save the file
4. **Restart Cursor** (important!)

### **Re-enable Later:**
1. Uncomment or add back the server entry
2. Save the file
3. **Restart Cursor**

---

## ✅ **Quick Fix Steps**

1. **Open MCP Config:**
   ```bash
   code ~/.cursor/mcp.json
   # or
   open ~/.cursor/mcp.json
   ```

2. **Remove Unused Servers:**
   - Keep: GitHub, Azure
   - Remove: Supabase, Vercel, Railway (if not needed)

3. **Save and Restart Cursor**

4. **Verify:**
   - Check tool count is under limit
   - Test that remaining servers work

---

## 💡 **Pro Tips**

1. **Enable on Demand**: Only enable servers when you need them
2. **Project-Specific**: Use different configs for different projects
3. **Check Tool Count**: Some servers have more tools than others
4. **Restart Required**: Always restart Cursor after changing MCP config

---

## 🚨 **If Still Exceeding Limit**

If you still exceed the limit with just 2 servers:

1. **Check Server Versions**: Newer versions may have more tools
2. **Use Specific Tools**: Some servers allow enabling only specific tools
3. **Contact Cursor Support**: The limit might be adjustable
4. **Use Alternative**: Use Azure CLI directly instead of MCP for Azure

---

**After fixing, restart Cursor and the error should be gone!** ✅

