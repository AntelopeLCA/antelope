"""
Authorization Tokens for XDB access

This file contains a routine for constructing JWT grant payloads from a set of grant specifications that satisfy
the class definition below.  These methods can be used to construct and interpret JWTs generated for interaction with
xdb and qdb servers.
"""

from pydantic import BaseModel
from typing import List, Dict
from collections import defaultdict
from datetime import datetime, timedelta


class ResourceSpec(BaseModel):
    origin: str
    source: str
    ds_type: str
    interfaces: List[str]
    static: bool
    options: Dict  # includes: priority=int, download={url: str, md5sum: Optional[str]}, token=str, possibly other ds-specific
    config: Dict[str, List[List]]  # must be a dict of config key: list of config value tuples (list of lists)


class GrantSpec(BaseModel):
    """
    A grant is assigned to an authorized user for a specific origin (including sub-origins) and interface.

    """
    username: str  # registered user who requested access
    origin: str  # origin to which access is granted
    interface: str  # interface to which access is granted

    grant_duration: int  # timedelta seconds

    qdb: bool  # whether requests can be forwarded to qdb
    values: bool  # whether numerical data can be requested
    update: bool  # whether user may alter the resource
    has_quota: bool  # whether user's activities are quota constrained (if true, xdb sends a receipt to auth server for every query)

    def serialize(self):
        s = [self.interface]
        if self.values:
            s.append('v')
        if self.update:
            s.append('u')
        if self.has_quota:
            s.append('Q')
        return ','.join(s)


class JwtGrant(BaseModel):
    """
    The contents of the JWT payload granted in response to a successful access request

    xdb must have or obtain a publickey from an established keyserver, corresponding with the contents of the iss field

    The signature is prepared using the private key associated with the issuer; xdb then verifies the signature
    with the public key

    the grants are used authorize the query
    """
    iss: str  # the authority providing the grant- must be known to the xdb via an established keyserver
    sub: str  # must specify the authorized user that is receiving the grant (bills back to)
    # (email address (if matches 'x@y') or vault.lc id (if matches 'x' or 'x@') of authorized user
    exp: int  # required

    grants: str  # specifies origins and permissions

    @classmethod
    def install_origins(cls, origins: List[str], sub: str, master_issuer: str, duration=60):
        """
        A token that is signed by the master issuer, specifying a list of origins to install from local resources
        :param origins:
        :param sub: the master issuer user
        :param master_issuer: the master issuer
        :param duration: lifetime for this token (default 60 seconds)
        :return:
        """
        the_grants = ' '.join(origins)
        exp = datetime.utcnow() + timedelta(seconds=duration)
        return cls(iss=master_issuer, sub=sub, exp=exp.timestamp(), grants=the_grants)

    @classmethod
    def from_grants(cls, grants: List[GrantSpec], issuer: str):
        """

        :param grants: Should be a list of GrantSpec subclasses
        :param issuer:
        :return:
        """

        origins = defaultdict(set)
        users = set()
        qdb = False
        dur = None
        for g in grants:
            users.add(g.username)
            qdb |= g.qdb
            if g.origin.startswith(issuer):
                origins[g.origin].add(g.serialize())
            if dur is None:
                dur = g.grant_duration
            else:
                dur = min([dur, g.grant_duration])

        if len(users) != 1:
            raise ValueError('Grants for multiple users received: %s' % users)

        user = users.pop()

        str_grants = []
        for o, gs in origins.items():
            str_grants.append('%s:%s' % (o, ':'.join(sorted(gs))))

        if qdb:
            str_grants.append('qdb')

        the_grants = ' '.join(str_grants)
        exp = datetime.utcnow() + timedelta(seconds=dur)

        return cls(iss=issuer, sub=user, exp=int(exp.timestamp()), grants=the_grants)


class IssuerKey(BaseModel):
    """
    An object of this class is sent to an xdb server to inform it of the information required to validate issuer tokens
    """
    issuer: str
    public_key: str
    expiry: datetime
