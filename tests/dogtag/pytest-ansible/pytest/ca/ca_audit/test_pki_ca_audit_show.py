"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Description: PKI CA-AUDIT CLI tests
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   The following pki ca-audit cli commands needs to be tested:
#   pki ca-audit-show
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Author: Pritam Singh <prisingh@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2019 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import logging

from pki.testlib.common.certlib import sys, os
from pki.testlib.common.utils import UserOperations
import pytest

try:
    from pki.testlib.common import constants
except Exception as e:
    if os.path.isfile('/tmp/test_dir/constants.py'):
        sys.path.append('/tmp/test_dir')
        import constants

userop = UserOperations(nssdb=constants.NSSDB)
log = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

TOPOLOGY = constants.CA_INSTANCE_NAME.split("-")[-2]


@pytest.mark.parametrize('args', ['--help', 'asdf', ''])
def test_pki_ca_audit_show_help(ansible_module, args):
    """
    :Title: Test pki ca-audit-show  --help command.
    :Description: test pki ca-audit-show --help command
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c
           SECret.123 -n "PKI CA Administrator for Example.Org"
           ca-audit-show --help
        2. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c
        SECret.123 -n "PKI CA Administrator for Example.Org"
        ca-audit-show asdf
        3. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c
        SECret.123 -n "PKI CA Administrator for Example.Org"
        ca-audit-show
    :Expected results:
        1. It should return help message.
        2. It should return exception
        3. It should return audit configuration
    """
    cmd_out = ansible_module.pki(cli="ca-audit-show",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(constants.CA_ADMIN_NICK),
                                 extra_args='{}'.format(args))
    for result in cmd_out.values():
        if args == '--help':
            assert result['rc'] == 0
            assert "usage: ca-audit-show [OPTIONS...]" in result['stdout']
            assert "--help" in result['stdout']
            assert "--output <file>" in result['stdout']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        elif args == 'asdf':
            assert result['rc'] >= 1
            assert 'ERROR: Too many arguments specified.' in result['stderr']
            log.info("Successfully run : '{}'".format(result['cmd']))
        elif args == '':
            assert result['rc'] == 0
            assert "Audit configuration" in result['stdout']
            log.info("Successfully ran : '{}'".format(result['cmd']))


def test_pki_ca_audit_show_for_non_existing_certificate_nickname(ansible_module):
    """
    :Title: pki ca-audit-show for non-existing certificate nickname
    :Description: Issue pki ca-audit-show for non exiting certificate nickname should fail
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
           -n "Nonexistingcertificate" ca-audit-show
    :Expected results:
        1. It should return a certificate not found exception

    """
    cmd_out = ansible_module.pki(cli="ca-audit-show",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='{}'.format("NonExistingCertificate"))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert 'RuntimeException: org.mozilla.jss.crypto.ObjectNotFoundException: ' \
                   'Certificate not found: NonExistingCertificate' in result['stderr']
            log.info("Successfully ran : {}".format(result['cmd']))
        else:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()


def test_pki_ca_audit_show_as_anonymous_user(ansible_module):
    """
    :Title: pki ca-audit-show as anonymous user
    :Description: Execute pki ca-audit-show as anonymous user should fail
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 ca-audit-show
    :Expected results:
        2. It should return unauthorised Exception

    """
    command = 'pki -d {} -c {} -h {} -P http -p {} ca-audit-show'.format(
        constants.NSSDB,
        constants.CLIENT_DIR_PASSWORD,
        constants.MASTER_HOSTNAME,
        constants.CA_HTTP_PORT)
    cmd_out = ansible_module.command(command)
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert 'PKIException: Unauthorized' in result['stderr']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()


def test_pki_ca_audit_show_with_output_option(ansible_module):
    """
    :Title: pki ca-audit-show with output option
    :Description: Issue pki ca-audit-show with output option and
                  verify output is generated
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
           -n "PKI CA Administrator for Example.Org" ca-audit-show --output auditconf
    :Expected results:
        1. It should generate a output with specific name

    """
    path = '/tmp/auditconf'
    cmd_out = ansible_module.pki(cli="ca-audit-show",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(constants.CA_ADMIN_NICK),
                                 extra_args='--output {}'.format(path))
    for result in cmd_out.values():
        if result['rc'] == 0:
            assert 'Stored audit configuration into {}'.format(path) in result['stdout']
            log.info('Successfully ran : {}'.format(result['cmd']))
            is_file = ansible_module.stat(path=path)
            for r1 in is_file.values():
                assert r1['stat']['exists']
        else:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()

    ansible_module.command('rm -rf {}'.format(path))


@pytest.mark.parametrize("valid_user_cert", ["CA_AdminV", "CA_AgentV", "CA_AuditV"])
def test_pki_ca_audit_show_with_valid_user_cert(valid_user_cert, ansible_module):
    """
    :Title: pki ca-audit-show with different valid user's cert
    :Description: Executing pki ca-audit-show using valid user cert should pass
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AdminV" ca-audit-show
        2. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AgentV" ca-audit-show
        3. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AuditV" ca-audit-show
    :Expected results:
        1. It should return Certificates

    """
    cmd_out = ansible_module.pki(cli="ca-audit-show",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(valid_user_cert))
    for result in cmd_out.values():
        if result['rc'] == 0:
            assert 'Audit configuration' in result['stdout']
            log.info('Successfully ran : {}'.format(result['cmd']))
        else:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()


@pytest.mark.parametrize("revoked_user_cert", ["CA_AdminR", "CA_AgentR", "CA_AuditR"])
def test_pki_ca_audit_show_with_revoked_user_cert(revoked_user_cert, ansible_module):
    """
    :Title: pki ca-audit-show with different revoked user's cert
    :Description: Executing pki ca-audit-show using revoked user cert
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AdminR" ca-audit-show
        2. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AgentR" ca-audit-show
        3. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AuditR" ca-audit-show
    :Expected results:
        1. It should throw an Exception.

    """
    cmd_out = ansible_module.pki(cli="ca-audit-show",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(revoked_user_cert))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert 'PKIException: Unauthorized' in result['stderr']
            log.info('Successfully ran : {}'.format(result['cmd']))
        else:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()


@pytest.mark.parametrize("expired_user_cert", ["CA_AdminE", "CA_AgentE", "CA_AuditE"])
def test_pki_ca_audit_show_with_expired_user_cert(expired_user_cert, ansible_module):
    """
    :Title: pki ca-audit-show with different user's expired cert
    :Description: Executing pki ca-audit-show using expired user cert
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AdminE" ca-audit-show
        2. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AgentE" ca-audit-show
        3. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
           -c SECret.123 -n "CA_AuditE" ca-audit-show
    :Expected results:
        1. It should return an Certificate Unknown Exception.

    """
    cmd_out = ansible_module.pki(cli="ca-audit-show",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(expired_user_cert))
    for result in cmd_out.values():
        if result['rc'] == 0:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()
        elif result['rc'] >= 1:
            assert "SEVERE: FATAL: SSL alert received: CERTIFICATE_EXPIRED\nIOException: " \
                   "SocketException cannot read on socket: Error reading from socket: " \
                   "(-12269) SSL peer rejected your certificate as expired." in result['stderr']
            log.info('Successfully ran : {}'.format(result['cmd']))


def test_pki_ca_audit_show_with_invalid_user(ansible_module):
    """
    :Title: pki ca-audit-show with invalid user's cert
    :Description: Issue pki ca-audit-show with invalid user
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
           -u pki_user -w Secret123 ca-audit-show
    :Expected results:
        1. It should return an Unauthorised Exception.

    """
    command_out = ansible_module.pki(cli="ca-audit-show",
                                     nssdb=constants.NSSDB,
                                     dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                     port=constants.CA_HTTP_PORT,
                                     authType='basicAuth',
                                     hostname=constants.MASTER_HOSTNAME,
                                     username='"{}"'.format("pki_user"),
                                     userpassword='"{}"'.format("Secret123"))
    for result in command_out.values():
        if result['rc'] >= 1:
            assert 'PKIException: Unauthorized' in result['stderr']
            log.info('Successfully ran : {}'.format(result['cmd']))
        else:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()


def test_pki_ca_audit_show_with_normal_user_cert(ansible_module):
    """
    :Title: pki ca-audit-show with normal user cert
    :Description: Issue pki ca-audit-show with normal user cert should fail
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. Add User
        2. Generate User Cert
        3. Add Cert to User
        4. Add User cert in database
        5. Show audit using the same user cert
    :Expected results:
        1. It should return an Forbidden Exception.
    """
    user = 'testUserCert'
    fullName = 'testUserCert'
    subject = "UID={},CN={}".format(user, fullName)
    userop.add_user(ansible_module, 'add', userid=user, user_name=fullName, subsystem='ca')
    cert_id = userop.process_certificate_request(ansible_module,
                                                 subject=subject,
                                                 request_type='pkcs10',
                                                 algo='rsa',
                                                 keysize='2048',
                                                 profile='caUserCert')
    ansible_module.pki(cli='ca-user-cert-add',
                       nssdb=constants.NSSDB,
                       dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                       port=constants.CA_HTTP_PORT,
                       hostname=constants.MASTER_HOSTNAME,
                       certnick='"{}"'.format(constants.CA_ADMIN_NICK),
                       extra_args='{} --serial {}'.format(user, cert_id))

    cert_import = 'pki -d {} -c {} -P http -p {} -h {} client-cert-import "{}" ' \
                  '--serial {}'.format(constants.NSSDB,
                                       constants.CLIENT_DIR_PASSWORD,
                                       constants.CA_HTTP_PORT,
                                       constants.MASTER_HOSTNAME, user,
                                       cert_id)
    ansible_module.command(cert_import)

    cmd_out = ansible_module.pki(cli="ca-audit-show",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(user))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert "ForbiddenException: Authorization Error" in result['stderr']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            log.error(result['stdout'])
            log.error(result['stderr'])
            pytest.fail()

    # Remove the cert from nssdb
    userop.remove_client_cert(ansible_module, user, subsystem='ca')

    # Remove the user
    userop.remove_user(ansible_module, user, subsystem='ca')
