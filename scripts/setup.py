"""Setup script for easy project initialization."""

import sys
from pathlib import Path


def main():
    """Run setup steps for the bot."""
    print("🤖 Discord Bot Template Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

    # Create .env if it doesn't exist
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if not env_path.exists() and env_example_path.exists():
        print("\n📝 Creating .env file from .env.example...")
        env_path.write_text(env_example_path.read_text())
        print("✅ .env file created")
        print("⚠️  Don't forget to add your DISCORD_TOKEN!")
    elif env_path.exists():
        print("\n✅ .env file already exists")
    else:
        print("\n❌ .env.example not found!")

    # Create required directories
    print("\n📁 Creating required directories...")
    directories = ["logs", "data", "bot/cogs"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}/")

    # Check if virtual environment is active
    print("\n🔍 Checking virtual environment...")
    if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("✅ Virtual environment is active")
    else:
        print("⚠️  No virtual environment detected")
        print("   Recommendation: Create one with 'python -m venv .venv'")

    # Check dependencies
    print("\n📦 Checking dependencies...")
    try:
        import discord
        print(f"✅ discord.py {discord.__version__} installed")
    except ImportError:
        print("❌ discord.py not installed")
        print("   Run: pip install -r requirements.txt")

    print("\n" + "=" * 50)
    print("✨ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env and add your DISCORD_TOKEN")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the bot: python main.py")
    print("\n📚 For more information, see README.md")


if __name__ == "__main__":
    main()
