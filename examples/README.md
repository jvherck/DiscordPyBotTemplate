# Examples

This directory contains examples demonstrating how to extend and customize the Discord bot template.

## Files

### `custom_bot.py`
Demonstrates how to create a custom bot by subclassing `DiscordBot`. Shows:
- Custom initialization
- Extended event handlers
- Background tasks with `discord.ext.tasks`
- Custom cleanup logic
- Working with the database

**Usage:**
```bash
python examples/custom_bot.py
```

### `custom_cog.py`
Comprehensive example of creating feature-rich cogs. Includes:
- Prefix commands and slash commands
- Command groups and subcommands
- Database interactions
- Cooldowns and permission checks
- Event listeners
- Error handling within cogs
- XP/leveling system example

**Usage:**
1. Copy to `bot/cogs/` directory:
   ```bash
   cp examples/custom_cog.py bot/cogs/example.py
   ```
2. Restart the bot - it will auto-load

## Learning Path

1. **Start with the base bot** (`main.py`)
   - Understand the basic structure
   - Learn how configuration works
   - Explore the existing cogs

2. **Study the example cog** (`custom_cog.py`)
   - See how to create different command types
   - Learn database integration patterns
   - Understand error handling

3. **Create a custom bot** (`custom_bot.py`)
   - Extend functionality while keeping base features
   - Add background tasks
   - Implement custom event handlers

4. **Build your own features**
   - Create new cogs for your specific needs
   - Extend the database models
   - Add custom configuration options

## Tips

- Always use type hints for better code quality
- Follow the async/await pattern consistently
- Use the bot's logger for debugging
- Take advantage of the database manager
- Test commands in a development server first
- Use guild-specific configs for multi-server bots

## Common Patterns

### Database Operations
```python
# Get
data = await self.bot.db.get(Model, id_value, "id_column")

# Create
new_item = Model(field=value)
await self.bot.db.create(new_item)

# Update
item.field = new_value
await self.bot.db.update(item)

# Delete
await self.bot.db.delete(item)
```

### Error Handling
```python
try:
    # Your code
    pass
except Exception as e:
    self.bot.logger.error(f"Error: {e}")
    await ctx.send("❌ An error occurred")
```

### Permission Checks
```python
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def my_command(self, ctx):
    pass
```

### Cooldowns
```python
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 use per 60 seconds per user
async def my_command(self, ctx):
    pass
```

## Need Help?

- Check the [main README](../README.md) for setup instructions
- Review the [discord.py documentation](https://discordpy.readthedocs.io/)
- Look at the existing cogs in `bot/cogs/`
- Join the [discord.py server](https://discord.gg/dpy)
