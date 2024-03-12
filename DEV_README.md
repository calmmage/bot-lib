# Dev README

Use tests to launch and debug functionality.

- [ ] Open this document in Obsidian

- [ ] integrate features developed as a part of fairytale-bot
  - [ ] set and get commands handler and builder
  - [ ] implement help message for help_command handler
 
## Telegram cool features
- [ ] extracting text from messages 
  - [ ] support voice messages and videos
  - [ ] forwards
    - [ ] collect all updates arriving SHORTLY after the original message (e.g. 100 ms?)
    - [ ] if command is missing inputs - wait for next message to arrive
  - [ ] replies 
    - option 1: us only latest message
    - option 2: use all messages in the chain / thread
- [ ] add a dev command to get back the last message as a python dict - for inspection
