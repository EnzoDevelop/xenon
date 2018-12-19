import discord

message_types = {
    None: ("", "{c}", "", 0x36393e),
    "info": ("Info", "{c}",
             "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678110-sign-info-512.png", 0x478fce),
    "wait_for": ("Waiting for response", "{c}", "https://cdn4.iconfinder.com/data/icons/small-n-flat/24/bubbles-alt2-512.png", 0x478fce),
    "success": ("Success!", "{c}", "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678134-sign-check-512.png",
                0x48ce6c),
    "warning": ("Warning", "{c}",
                "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678136-shield-warning-512.png",
                0xefbc2f),
    "working": ("Please wait ...", "{c}",
                "https://cdn.discordapp.com/attachments/481121629926064129/516295519920848919/amiloader.gif",
                0x36393e),
    "error": ("Error", "{c}" + f"\n\n[Support](https://discord.gg/SpZPkPf)",
              "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678069-sign-error-512.png",
              0xc64935),
    "perm_error": ("Insufficient Permission", "{c}",
                   "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678069-sign-error-512.png",
                   0xc64935),
    "unex_error": ("Error", "**Error Code:**\n```{c}```" + f"\n\n[Support](https://discord.gg/SpZPkPf)",
                   "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678069-sign-error-512.png", 0xc64935)
}


def embed_message(content=None, title=None, type=None):
    emb_title, content_format, icon, color = message_types.get(type) or message_types.get(None)
    title = title or emb_title
    embed = discord.Embed(color=discord.Color(color), description=content_format.format(c=content))
    embed.set_author(name=title, icon_url=icon)
    return {"embed": embed}


def paginate(content, limit=1900):
    result = [""]
    lines = content.splitlines(keepends=True)
    i = 0
    for line in lines:
        if len(result[i]) + len(line) <= limit:
            result[i] += line

        else:
            i += 1
            result.append(line)

    return result


def clean(content):
    return ''.join(e for e in content if e.isalnum())
