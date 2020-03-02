#!/usr/bin/python
# -*- coding: utf-8 -*-



# import scripts.runit as run


jira_options = {'server':'https://jira.infinet.ru/'}
jira = JIRA(options=jira_options, basic_auth=())

# new_issue = jira.create_issue(project='DESK', summary='Test jira', description='Blablabla', issuetype={'name': 'Support Request'})


# report = ['----------------------------------------------------------------------------------------------------\nParsing diagnostic card: F:\\Parser\\scripts\\dcards\\diagcard.SN-506026 xg 1000 link up and all ok.txt\n----------------------------------------------------------------------------------------------------\n', 'Serial Number is 506026\nModel is Xm/5X.1000.4x300.2x23\n', 'Test results:\n', 'The 506026 device is fine']
# report = ''.join(report)
# comment = jira.add_comment('DESK-53647', report)

issue = jira.issue('DESK-53647')

for attachment in issue.fields.attachment:
    print("Name: '{filename}', size: {size}".format(
            filename=attachment.filename, size=attachment.size))
    # to read content use `get` method:
    print("Content: '{}'".format(attachment.get()))