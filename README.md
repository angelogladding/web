# web
tools for metamodern web development

## Bootstrap a host

*NOTE: replace example.org with your domain name*

1) Create a new Debian 10 machine (at your host)
2) Point your domain name to your machine's IP address (at your registrar)
3) Run `ssh -tt root@example.org "wget https://raw.githubusercontent.com/angelogladding/web/main/host.py -qO host.py && python3 host.py"` in your terminal and copy the resulting token
4) Navigate to `https://example.org:5555` in your browser and paste the token
