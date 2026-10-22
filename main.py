import os
import subprocess
import sys

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def health():
    return 'ok'


@app.route('/getlink', methods=['POST'])
def get_link():
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()

    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    if not url.startswith(('http://', 'https://')):
        return jsonify({'error': 'URL inválida'}), 400

    try:
        result = subprocess.run(
            [
                sys.executable, '-m', 'yt_dlp',
                '-g',                        # solo imprime la URL directa
                '--no-playlist',
                '-f', 'best[ext=mp4]/best',  # UN solo archivo (video+audio juntos)
                '--', url,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'yt-dlp tardó demasiado'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if result.returncode != 0:
        lines = result.stderr.strip().splitlines()
        return jsonify({'error': lines[-1] if lines else 'yt-dlp falló'}), 500

    links = result.stdout.strip().splitlines()
    if not links:
        return jsonify({'error': 'No se obtuvo ningún link'}), 500

    return jsonify({'link': links[0]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
