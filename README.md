# web
tools for metamodern web development

## Bootstrap a host

1) Create a new Debian 10 machine (at your host) noting its IP address
2) Point your domain name to this IP address (at your registrar)
3) Run `ssh -tt root@YOUR.DOMAIN "wget https://raw.githubusercontent.com/angelogladding/web/main/host.py -qO host.py && python3 host.py"` in your terminal and copy the resulting token
4) Navigate to `http://YOUR.DOMAIN:5555` in your browser and paste the token
