# 🔒 Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Updates

### Latest Release (December 2024)

All known vulnerabilities have been patched:

✅ **Fixed Vulnerabilities**:
- CVE-2020-14152 (Fiona/zlib) - Updated fiona to >= 1.10b2
- CVE-2023-45853 (Fiona/MiniZip) - Updated fiona to >= 1.10b2
- Buffer overflow in Pillow - Updated to >= 10.3.0

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please contact the maintainer directly:

- **LinkedIn**: https://www.linkedin.com/in/ruan-almeida-8b8136295/

Include in your report:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

You should expect:
- Acknowledgment within 48 hours
- Status update within 7 days
- Fix released within 30 days (for confirmed vulnerabilities)

## Security Best Practices

### For Developers

1. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Scan for vulnerabilities**:
   ```bash
   pip install safety
   safety check -r requirements.txt
   ```

3. **Never commit secrets**:
   - Use `.gitignore` for sensitive files
   - Use environment variables or secrets management
   - Review commits before pushing

### For Deployment

1. **Use HTTPS** in production
2. **Enable authentication** on Streamlit
3. **Restrict file access** (proper permissions)
4. **Regular updates** of all dependencies
5. **Monitor logs** for suspicious activity
6. **Backup data** regularly

### Data Protection (LGPD)

When handling CPF/CNPJ data:

1. **Anonymize** before sharing:
   ```python
   import hashlib
   cpf_hash = hashlib.sha256(cpf.encode()).hexdigest()
   ```

2. **Obtain consent** from data subjects
3. **Implement access controls**
4. **Encrypt sensitive data** at rest
5. **Audit access logs**

## Dependency Security

Current dependency versions (patched):

| Dependency | Version | Security Status |
|------------|---------|-----------------|
| fiona | >= 1.10b2 | ✅ Patched (CVE-2020-14152, CVE-2023-45853) |
| Pillow | >= 10.3.0 | ✅ Patched (Buffer overflow) |
| streamlit | 1.31.0 | ✅ No known vulnerabilities |
| geopandas | 0.14.2 | ✅ No known vulnerabilities |
| pandas | 2.2.0 | ✅ No known vulnerabilities |
| folium | 0.15.1 | ✅ No known vulnerabilities |
| plotly | 5.18.0 | ✅ No known vulnerabilities |
| reportlab | 4.0.9 | ✅ No known vulnerabilities |
| requests | 2.31.0 | ✅ No known vulnerabilities |

### Automatic Security Checks

This project uses GitHub Actions to:
- Check Python syntax on every push
- Validate requirements.txt format
- (Future) Run security scanners

## Changelog

### v1.0.1 (December 2024)
- 🔒 **Security**: Updated fiona to >= 1.10b2 (fixes CVE-2020-14152, CVE-2023-45853)
- 🔒 **Security**: Updated Pillow to >= 10.3.0 (fixes buffer overflow)

### v1.0.0 (December 2024)
- 🎉 Initial release
- ✅ All features implemented
- ✅ Complete documentation

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [LGPD (Brazil)](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
- [Streamlit Security](https://docs.streamlit.io/knowledge-base/deploy/authentication)

---

**Last Updated**: December 2024
