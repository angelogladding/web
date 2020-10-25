# web
tools for metamodern web development

## Bootstrap a host

*NOTE: replace example.org with your domain name*

1) Create a new Debian 10 machine (at your host)
2) Point your domain name to your machine's IP address (at your registrar)
3) Run `ssh root@example.org "wget https://raw.githubusercontent.com/angelogladding/web/main/bootstrap.py && python3 bootstrap.py"` in your terminal and copy the resulting token
4) Navigate to `https://example.org:5555` in your browser and paste the token
