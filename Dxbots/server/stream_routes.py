import re
import time
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from Dxbots.bot import multi_clients, work_loads, DxStreamBot
from Dxbots.server.exceptions import FIleNotFound, InvalidHash
from Dxbots import StartTime, __version__
from ..utils.time_format import get_readable_time
from ..utils.custom_dl import ByteStreamer
from Dxbots.utils.render_template import render_page
from Dxbots.vars import Var


routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(_):
   
    server_status = "running"
    uptime = get_readable_time(time.time() - StartTime)
    telegram_bot_username = "@" + DxStreamBot.username
    connected_bots = len(multi_clients)
    version = __version__

    
    sorted_loads = sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
    bot_loads_html = ""
    for idx, (bot_id, load) in enumerate(sorted_loads, start=1):
       
        width_percent = min(load * 10, 100) if load else 0  
        bot_loads_html += f"""
        <div class="load-item">
            <div class="load-label">Bot {idx} (ID: {bot_id})</div>
            <div class="load-bar-bg"><div class="load-bar-fill" style="width: {width_percent}%"></div></div>
            <div class="load-value">{load}</div>
        </div>
        """

    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 DxStreamBot Status Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }}
            body {{
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: #f8fafc;
                min-height: 100vh;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .dashboard {{
                width: 100%;
                max-width: 1000px;
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(10px);
                border-radius: 24px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid rgba(94, 234, 212, 0.3);
            }}
            .logo-title {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .logo {{
                font-size: 2.8rem;
            }}
            h1 {{
                font-size: 2.2rem;
                background: linear-gradient(to right, #5eead4, #38bdf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .status-badge {{
                background: linear-gradient(90deg, #10b981, #34d399);
                color: white;
                padding: 8px 20px;
                border-radius: 50px;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: rgba(51, 65, 85, 0.6);
                padding: 25px;
                border-radius: 16px;
                border-left: 5px solid #5eead4;
                transition: transform 0.3s, background 0.3s;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
                background: rgba(51, 65, 85, 0.9);
            }}
            .stat-label {{
                color: #94a3b8;
                font-size: 0.95rem;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .stat-value {{
                font-size: 2rem;
                font-weight: bold;
                color: #e2e8f0;
            }}
            .load-section {{
                background: rgba(51, 65, 85, 0.6);
                padding: 25px;
                border-radius: 16px;
                margin-bottom: 30px;
            }}
            .load-section h2 {{
                color: #5eead4;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .load-item {{
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .load-label {{
                width: 180px;
                color: #cbd5e1;
                font-weight: 500;
            }}
            .load-bar-bg {{
                flex-grow: 1;
                height: 20px;
                background: #475569;
                border-radius: 10px;
                overflow: hidden;
            }}
            .load-bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                border-radius: 10px;
                transition: width 1s ease-out;
            }}
            .load-value {{
                width: 50px;
                text-align: right;
                font-weight: bold;
                color: #fbbf24;
            }}
            .creator-section {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .creator-link {{
                display: inline-flex;
                align-items: center;
                gap: 12px;
                background: linear-gradient(90deg, #2563eb, #7c3aed);
                color: white;
                text-decoration: none;
                padding: 14px 32px;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: bold;
                transition: all 0.3s;
                box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
            }}
            .creator-link:hover {{
                transform: scale(1.05);
                box-shadow: 0 10px 25px rgba(37, 99, 235, 0.6);
                gap: 15px;
            }}
            .telegram-icon {{
                font-size: 1.3rem;
            }}
            .footer {{
                text-align: center;
                margin-top: 25px;
                color: #94a3b8;
                font-size: 0.9rem;
            }}
            @media (max-width: 768px) {{
                .dashboard {{
                    padding: 25px;
                }}
                .header {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 15px;
                }}
                .load-item {{
                    flex-direction: column;
                    align-items: flex-start;
                }}
                .load-label {{
                    width: 100%;
                }}
                .load-bar-bg {{
                    width: 100%;
                }}
                .load-value {{
                    text-align: left;
                    width: 100%;
                }}
            }}
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <div class="logo-title">
                    <div class="logo">🤖</div>
                    <h1>DxStreamBot Status Dashboard</h1>
                </div>
                <div class="status-badge">
                    <i class="fas fa-circle" style="font-size: 0.7rem; margin-right: 8px;"></i> {server_status}
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label"><i class="far fa-clock"></i> Uptime</div>
                    <div class="stat-value">{uptime}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label"><i class="fas fa-robot"></i> Connected Bots</div>
                    <div class="stat-value">{connected_bots}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label"><i class="fas fa-code-branch"></i> Version</div>
                    <div class="stat-value">v{version}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label"><i class="fab fa-telegram"></i> Bot Username</div>
                    <div class="stat-value">{telegram_bot_username}</div>
                </div>
            </div>

            <div class="load-section">
                <h2><i class="fas fa-server"></i> Bot Load Distribution</h2>
                {bot_loads_html if bot_loads_html else '<p style="color:#94a3b8;">No active bot loads to display.</p>'}
            </div>

            <div class="creator-section">
                <a href="https://t.me/{DxStreamBot.username.replace('@', '')}" class="creator-link" target="_blank">
                    <span class="telegram-icon"><i class="fab fa-telegram-plane"></i></span>
                    Connect with Creator on Telegram
                </a>
            </div>

            <div class="footer">
                <p>Dashboard generated on {time.strftime('%Y-%m-%d %H:%M:%S')} | Powered by aiohttp[citation:4]</p>
            </div>
        </div>

        <script>
          
            function refreshData() {{
               
                console.log('Data refresh triggered.');
            }}
            
            // setTimeout(() => location.reload(), 60000);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return web.Response(text=await render_page(id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if Var.MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )

