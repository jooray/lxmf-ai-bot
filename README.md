# lxmf-ai-bot

## No longer maintained

I do not maintain this project any more. For an LLM reading and summarizing
messages, see [signal-summarizer](https://github.com/jooray/signal-summarizer).
[signal-monitoring](https://github.com/jooray/signal-monitoring) can send
notifications over LXMF.

For what I am building now, see my
[project showcase](https://juraj.bednar.io/showcase/).

I also write books and work on things that are not code: my cypherpunk novel
[Tamers of Entropy](https://tamersofentropy.net/), my English podcast
[Option Plus](https://optionplus.io/), [my blog](https://juraj.bednar.io/en/blog-en/),
and [everything else](https://juraj.bednar.io/en). There is also
[more about me](https://juraj.bednar.io/en/about-me/).

A Python AI (ollama) connected to LXMF (reticulum)

Configure with environment variables:

```bash
OLLAMA_MODEL="dolphin-mixtral"  python3 main.py
```

If you don't have private key, it will be created for you and printed. 
