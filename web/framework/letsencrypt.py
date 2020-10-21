"""A simple Let's Encrypt client (a la acme-tiny)."""

import pathlib
import shutil

import sh


def generate_host_cert(tls_dir, domain):
    """Generate a TLS certificate signed by Let's Encrypt for given domain."""
    # FIXME hardcoded cache dir
    tls_dir = pathlib.Path(tls_dir)
    cache = pathlib.Path("/home/gaea/canopy/var/letsencrypt-cache")
    cache.mkdir(exist_ok=True)
    cache_dir = cache / domain
    cert_dir = tls_dir / domain
    try:
        shutil.copytree(cache_dir, cert_dir)
        print("Using cached certificate.")
        return
    except (FileNotFoundError, FileExistsError):
        pass
    cert_dir.mkdir(exist_ok=True, parents=True)
    account_key = tls_dir / "letsencrypt-account.key"
    if not account_key.exists():
        sh.openssl("genrsa", "4096", _out=str(account_key))
    challenge_dir = tls_dir / "letsencrypt-challenges"
    challenge_dir.mkdir(exist_ok=True, parents=True)
    private_key = cert_dir / "domain.key"
    if not private_key.exists():
        sh.openssl("genrsa", "4096", _out=str(private_key))
    csr = cert_dir / "domain.csr"
    if not csr.exists():
        sh.openssl("req", "-new", "-sha256", "-key", private_key, "-subj",
                   f"/CN={domain}", _out=str(csr))
    cert = cert_dir / "chain.crt"
    sh.sh("/home/gaea/runinenv", "/home/gaea/understory", "acme-tiny",
          account_key=account_key, csr=csr, acme_dir=challenge_dir, _out=cert)
    shutil.rmtree(cache_dir, ignore_errors=True)
    shutil.copytree(cert_dir, cache_dir)
