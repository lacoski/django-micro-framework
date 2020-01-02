from django.core.management.base import BaseCommand, CommandError

from micro_framework.jwt_auth.models import Policy


class Command(BaseCommand):
    help = 'Delete Policy for service'

    def delete_service_policy(self, policy_name):
        Policy.objects.get(name=policy_name).delete()

    def add_arguments(self, parser):
        parser.add_argument('policyname', type=str)

    def handle(self, *args, **kwargs):
        policy_name = kwargs['policyname']

        try:
            Policy.objects.get(name=policy_name).delete()
        except Exception as ex:
            raise CommandError(
                'Cannot delete the Policy ({}) '.format(
                    policy_name)
            )
        self.stdout.write(
            'Delete Policy ({})'.format(policy_name))
