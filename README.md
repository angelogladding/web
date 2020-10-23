# web

## Bootsrap your host

*replace example.org with your domain name*

*replace J39ce4wx8K with the token generated at the end of your bootstrap*

Point your domain name (at your registrar) to the IP address of a machine with a Debian 10 installation (at your host).

    ssh root@example.org "wget https://raw.githubusercontent.com/angelogladding/web/master/bootstrap.py && python3 bootstrap.py"
    J39ce4wx8K

Use that token to sign in to your host administration interface:

    https://example.org:5555/?token=J39ce4wx8K
