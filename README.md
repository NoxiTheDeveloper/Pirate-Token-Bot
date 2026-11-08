# Pirate Token Bot 🏴‍☠️

A simple Fortnite automation bot that handles the process of leaving matches, returning to the lobby and readying up for the next game.

It uses Python and OpenCV to recognise Fortnite's UI and automatically interact with the game, meaning you don't have to manually go through the same menus every time.

## Features

• Automatic match detection

• Automatically leaves completed matches

• Returns to the Fortnite lobby

• Automatically presses READY

• Recognises UI elements using OpenCV

• Randomised idle movement

• Detects player input and pauses movement

• Custom screenshot setup for UI recognition

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/NoxiTheDeveloper/Pirate-Token-Bot.git
```

**2. Open the project folder**

```bash
cd Pirate-Token-Bot
```

**3. Install the required packages**

```bash
pip install -r requirements.txt
```

**4. Run the bot**

```bash
python "Pirate Token Bot.py"
```

That's it! The bot will start up and check that all required image templates are available.

## First Time Setup

The bot needs screenshots of a few Fortnite UI elements so it knows what to look for.

If the images are missing, it will ask you to capture them.

| File | What to capture |
|:---|:---|
| `placed.png` | YOU PLACED text |
| `menu.png` | Three line menu button |
| `lobby.png` | Return to Lobby button |
| `ready.png` | Yellow READY button |

When prompted:

1. Get the relevant UI element on screen.
2. Press `F8`.
3. Drag a box around the element.
4. Press `ENTER` to save it.
5. Repeat for the remaining images.

Keep all screenshots in the same folder as the Python file.

## Controls

| Key | Action |
|:---|:---|
| `F8` | Capture UI screenshot |
| `F9` | Toggle idle movement |
| `CTRL + C` | Stop the bot |

The bot also detects when you're using your keyboard or mouse and pauses its idle movement.

## Useful Commands

**Recapture UI images**

```bash
python "Pirate Token Bot.py" setup
```

**Test image recognition**

```bash
python "Pirate Token Bot.py" test
```

**Check available image files**

```bash
python "Pirate Token Bot.py" files
```

## Troubleshooting

**Bot can't recognise buttons**

Make sure your screenshots match your current Fortnite UI. If you've changed resolution or settings, try capturing them again.

**Missing image files**

Run the setup command to capture any missing screenshots.

**Bot isn't detecting Fortnite**

Make sure Fortnite is running on your primary monitor.

## Disclaimer

Pirate Token Bot is an independent project and is not affiliated with, endorsed by or sponsored by Epic Games, Inc.

Fortnite and all related trademarks belong to their respective owners.

Use at your own discretion. Third party automation may be against Epic Games' Terms of Service.

## Credits

Made by [NoxiTheDeveloper](https://github.com/NoxiTheDeveloper)

If you like the project, consider leaving a ⭐ on the repository!
