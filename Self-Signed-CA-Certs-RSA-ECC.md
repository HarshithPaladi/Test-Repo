# SSL Certificates Cheat-Sheet

X.509 is an ITU standard defining the format of public key certificates. X.509 are used in TLS/SSL, which is the basis for HTTPS. An X.509 certificate binds an identity to a public key using a digital signature. A certificate contains an identity (hostname, organization, etc.) and a public key (RSA, DSA, ECDSA, ed25519, etc.), and is either signed by a Certificate Authority or is Self-Signed.

# Self-Signed Certificates

## RSA 
### Generate CA
1. Generate RSA Private key
```bash
openssl genrsa -aes256 -out ca-key.pem 4096
```
> Here, `-aes256` is encrypting the private key with aes256 encryption
2. Generate a public CA Cert
```bash
openssl req -new -x509 -sha256 -days 36500 -key ca-key.pem -out ca.pem
```
> Here `-days` can be anything we want, I kept a 100 years for this markdown

### Generate Certificate
1. Create a RSA key
```bash
openssl genrsa -out cert-key.pem 4096
```
2. Create a Certificate Signing Request (CSR)
```bash
openssl req -new -sha256 -subj "/CN=Certdomain" -key cert-key.pem -out cert.csr
```
> Here, in `-subj` the certdomain can be anything. It will be better to give it the domain name for which the certificate is being generated
3. Create a `extfile.cnf` with all the alternative names
```bash
# inside the extfile
subjectAltName = @alt_names
[alt_names]
DNS.0 = test.harshith
DNS.1 = *.test.harshith
IP.0 = someip
IP.1 = someotherip
```
```bash
# optional
echo extendedKeyUsage = serverAuth >> extfile.cnf
```
4. Create the certificate
```bash
openssl x509 -req -sha256 -days 36500 -in cert.csr -CA ca.pem -CAkey ca-key.pem -out cert.pem -extfile extfile.cnf
```
5. Bundle the certificates to create a bundle  
    **Order of the certs in the bundle**  
        1. Certificate  
        2. CA Certificate
    ```bash
    cat cert.pem >> rsa-4096-bundle.pem
    ```
    Replace certificate.pem with its actual location and name
    ```bash
    cat certificate.pem >> rsa-4096-bundle.pem
    ```
## ECC
### Generate CA
1. Generate Private Key for the CA  
    ```bash
    openssl ecparam -genkey -name secp521r1 -out private-key.pem
    ```
1. Create a Certificate signing request
    ```bash
    openssl req -new -key private-key.pem -out csr.csr
    ```
1. Sign the Certificate Signing request with the private key to create a certificate
    ```bash
    openssl req -x509 -nodes -days 36500 -key private-key.pem -in csr.csr -out certificate.pem
    ```
1. Check the connection with the openssl
    ```bash
    openssl s_client -connect test.harshith:443
    ```
### Generate Certificate
1. Create the private key  
    > see `openssl ecparam -list_curves` for all the available curves for the `-name `parameter
    ```bash
    openssl ecparam -genkey -name prime256v1 -out private-key.pem
    ```
1. Create a Certificate signing request
    ```bash
    openssl req -new -key private-key.pem -out cert.csr
    ```
1. Create an extfile.conf for the certificate parameters
    ```bash
    # Inside the extfile.conf

    subjectAltName = @alt_names
    [alt_names]
    DNS.0 = test.harshith
    DNS.1 = *.test.harshith
    IP.0 = someip
    IP.1 = someotherip
    ```
1. Sign the Certificate Signing request with the private key to create a certificate
    ```bash
    openssl x509 -req -sha256 -days 36500 -in cert.csr -CA ~/docker/self-signed/certs/ECC-CA/certificate.pem -CAkey ~/docker/self-signed/certs/ECC-CA/private-key.pem -out cert.pem -extfile extfile.conf -CAcreateserial
    ```
    > cert.pem is the certificate signed by the private key of the CA  
    
1. Bundle the certificates to create a bundle  
    **Order of the certs in the bundle**  
        1. Certificate  
        2. CA Certificate
    ```bash
    cat cert.pem >> ecc-256-bundle.pem
    ```
    Replace certificate.pem with its actual location and name
    ```bash
    cat certificate.pem >> ecc-256-bundle.pem
    ```
## Certificate Formats

X.509 Certificates exist in Base64 Formats **PEM (.pem, .crt, .ca-bundle)**, **PKCS#7 (.p7b, p7s)** and Binary Formats **DER (.der, .cer)**, **PKCS#12 (.pfx, p12)**.

### Convert Certs

COMMAND | CONVERSION
---|---
`openssl x509 -outform der -in cert.pem -out cert.der` | PEM to DER
`openssl x509 -inform der -in cert.der -out cert.pem` | DER to PEM
`openssl pkcs12 -in cert.pfx -out cert.pem -nodes` | PFX to PEM

## Verify Certificates
`openssl verify -CAfile ca.pem -verbose cert.pem`

## Install the CA Cert as a trusted root CA

### On Debian & Derivatives
> Copy the `ca.pem` as `ca.crt` and then move `ca.crt` into the `/usr/local/share/ca-certificates/`
- Move the CA certificate (`ca.pem`) into `/usr/local/share/ca-certificates/ca.crt`.
- Update the Cert Store with:
    ```bash
    sudo update-ca-certificates
    ```

Refer the documentation [here](https://wiki.debian.org/Self-Signed_Certificate) and [here.](https://manpages.debian.org/buster/ca-certificates/update-ca-certificates.8.en.html)
### On Windows

Assuming the path to your generated CA certificate as `C:\ca.pem`, run:
```powershell
Import-Certificate -FilePath "C:\ca.pem" -CertStoreLocation Cert:\LocalMachine\Root
```
- Set `-CertStoreLocation` to `Cert:\CurrentUser\Root` in case you want to trust certificates only for the logged in user.

OR

In Command Prompt, run:
```sh
certutil.exe -addstore root C:\ca.pem
```

- `certutil.exe` is a built-in tool (classic `System32` one) and adds a system-wide trust anchor.

### On Android

The exact steps vary device-to-device, but here is a generalised guide:
1. Open Phone Settings
2. Locate `Encryption and Credentials` section. It is generally found under `Settings > Security > Encryption and Credentials`
3. Choose `Install a certificate`
4. Choose `CA Certificate`
5. Locate the certificate file `ca.pem` on your SD Card/Internal Storage using the file manager.
6. Select to load it.
7. Done!

## Credits : 
- Markdown [The Digital Life Github (xcad2k)](https://github.com/xcad2k/cheat-sheets/blob/main/misc/ssl-certs.md)
    - [YT Link for the video](https://youtu.be/VH4gXcvkmOY) 
- Full ECC Writeup on this [link](https://www.golinuxcloud.com/openssl-generate-ecc-certificate/#5_Create_CA_certificate_with_ECC_Key) (ECC CA and certificate)
    - Alternate [link](https://web.archive.org/web/20210507111239/https://www.golinuxcloud.com/openssl-generate-ecc-certificate/)
- Extfile.conf taken from this [link](https://community.f5.com/t5/technical-articles/building-an-openssl-certificate-authority-creating-ecc/ta-p/279468)
## Other Useful References :
- Create self-signed ECDSA (ECC) certificate with private key inside in openssl [link](https://gist.github.com/marta-krzyk-dev/83168c9a8e985e5b3b1b14a98b533b9c)
- How to setup your own CA with OpenSSL [link](https://gist.github.com/Soarez/9688998)
- How To Create an ECC Certificate on Nginx for Debian 8 [link](https://www.digitalocean.com/community/tutorials/how-to-create-an-ecc-certificate-on-nginx-for-debian-8)
