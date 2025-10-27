#!/usr/bin/env bash
set -e
cd /home/kubanych/dishrank
source venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1 || true
sudo systemctl restart dishrank
systemctl --no-pager --quiet is-active dishrank && echo "✅ DishRank restarted"
