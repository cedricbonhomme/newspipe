import logging
from urllib.parse import urlparse

import ldap3
from ldap3.core.exceptions import LDAPBindError
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .abstract import AbstractController
from newspipe.bootstrap import application
from newspipe.models import User

# from ldap3.core.exceptions import LDAPPasswordIsMandatoryError

# FOR LDAP
# Reference: session_app

logger = logging.getLogger(__name__)


class UserController(AbstractController):
    _db_cls = User
    _user_id_key = "id"

    def _handle_password(self, attrs):
        if attrs.get("password"):
            attrs["pwdhash"] = generate_password_hash(attrs.pop("password"))
        elif "password" in attrs:
            del attrs["password"]

    def check_password(self, user, password):
        return check_password_hash(user.pwdhash, password)

    def create(self, **attrs):
        self._handle_password(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs):
        self._handle_password(attrs)
        return super().update(filters, attrs)


class LdapuserController:
    def check_password(self, user, password, config):
        this_uri = self.get_next_ldap_server(config)
        # return this_uri
        this_user = self.list_matching_users(
            server_uri=this_uri,
            bind_dn=config["LDAP_BIND_DN"],
            bind_pw=config["LDAP_BIND_PASSWORD"],
            user_base=config["LDAP_USER_BASE"],
            username=user,
            user_match_attrib=config["LDAP_USER_MATCH_ATTRIB"],
            _filter=config["LDAP_FILTER"] if "LDAP_FILTER" in config else "",
        )
        # list_matching_users always returns list, so if it contains <> 1 we are in trouble
        if len(this_user) != 1:
            print(
                f"WARNING: cannot determine unique user for"
                f" {config['LDAP_USER_MATCH_ATTRIB']}={user} which returned {this_user}"
            )
            return False
        # logger does not work here+flask for some reason. Very sad!
        # now we have exactly one user, this_user[0]
        this_user = this_user[0]

        ldapuser = self.authenticated_user(
            server_uri=this_uri, user_dn=this_user, password=password
        )
        if ldapuser:
            return ldapuser
        # return str(config)
        # return this_user
        return False

    def get_next_ldap_server(self, config):
        # on first ldap_login attempt, cache this lookup result:
        if "LDAP_HOSTS" not in config:
            this_domain = urlparse(config["LDAP_URI"]).hostname
            config["LDAP_HOSTS"] = self.list_ldap_servers_for_domain(this_domain)
        else:
            # rotate them! So every ldap_login attempt will use the next ldap server in the list.
            this_list = config["LDAP_HOSTS"]
            a = this_list[0]
            this_list.append(a)
            this_list.pop(0)
            config["LDAP_HOSTS"] = this_list
        # construct a new, full uri.
        this_netloc = config["LDAP_HOSTS"][0]
        up = urlparse(config["LDAP_URI"])
        if up.port:
            this_netloc += f":{up.port}"
        this_uri = up._replace(netloc=this_netloc).geturl()
        return this_uri

    def list_matching_users(
        self,
        server_uri="",
        bind_dn="",
        bind_pw="",
        connection=None,
        user_base="",
        username="",
        user_match_attrib="",
        _filter="",
    ):
        search_filter = f"({user_match_attrib}={username})"
        if _filter:
            search_filter = f"(&{search_filter}{_filter})"
        if connection and isinstance(connection, ldap3.core.connection.Connection):
            conn = connection
        else:
            conn = self.get_ldap_connection(server_uri, bind_dn, bind_pw)
        conn.search(
            search_base=user_base, search_filter=search_filter, search_scope="SUBTREE"
        )
        print(f"DEBUG: search_base {user_base}")
        print(f"DEBUG: search_filter {search_filter}")
        result = []
        for i in conn.entries:
            result.append(i.entry_dn)
        print(f"DEBUG: result {result}")
        return result

    def get_ldap_connection(self, server_uri, bind_dn, bind_pw):
        server = ldap3.Server(server_uri)
        conn = ldap3.Connection(server, auto_bind=True, user=bind_dn, password=bind_pw)
        return conn

    def list_ldap_servers_for_domain(self, domain):
        # return list of hostnames from the _ldap._tcp.{domain} SRV lookup
        try:
            import dns
            import dns.resolver
        except Exception:
            print("Need python3-dns or dnspython installed for dns lookups.")
            return [domain]
        namelist = []
        try:
            query = dns.resolver.query(f"_ldap._tcp.{domain}", "SRV")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            # no records exist that match the request, so we were probably
            # given a specific hostname, and an empty query will trigger
            # the logic below that will add the original domain to the list.
            query = []
        for i in query:
            namelist.append(i.target.to_text().rstrip("."))
        if not len(namelist):
            namelist.append(domain)
        return namelist

    def ldap_login(self, username, password):
        # print(f"DEBUG: Trying user {username} with pw '{password}'")
        this_uri = self.get_next_ldap_server(application.config)
        # Perform the ldap interactions
        user = self.authenticated_user(
            server_uri=this_uri, user_dn=username, password=password
        )
        if user:
            return user
        else:
            return False

    def authenticated_user(self, server_uri, user_dn, password):
        print(f"server_uri: {server_uri}")
        print(f"user_dn: {user_dn}")
        try:
            conn = self.get_ldap_connection(server_uri, user_dn, password)
            return conn
        except LDAPBindError as e:
            if "invalidCredentials" in str(e):
                print("Invalid credentials.")
                return False
            else:
                raise e
        # except (LDAPPasswordIsMandatoryError, LDAPBindError):
        #   print("Either an ldap password is required, or we had another bind error.")
        #   return False
