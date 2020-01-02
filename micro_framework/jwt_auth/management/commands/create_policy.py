from django.core.management.base import BaseCommand, CommandError

from micro_framework.jwt_auth.models import Policy


class Command(BaseCommand):
    help = 'Create Policy for service'

    def create_service_policy(self, policy_name, policy_rule):
        policy = Policy.objects.get_or_create(name=policy_name, rules=policy_rule)
        return policy[0]

    def add_arguments(self, parser):
        parser.add_argument('policyname', type=str)
        parser.add_argument('policyrule', type=str)

    def handle(self, *args, **kwargs):
        policy_name = kwargs['policyname']
        policy_rule = kwargs['policyrule']

        try:
            token = self.create_service_policy(policy_name, policy_rule)
        except Exception as ex:
            raise CommandError(
                'Cannot create the Policy {} '.format(
                    policy_name)
            )
        self.stdout.write(
            'Created Policy ({}) with rule ({})'.format(policy_name, policy_rule))
