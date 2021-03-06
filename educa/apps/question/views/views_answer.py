from django.http import HttpResponse

from educa.apps.question.forms import AnswerForm
from educa.apps.question.models import Answer
from educa.mixin.question import QuestionViewMixin, AnswerMixin
from educa.utils.utils import render_error


class AnswerCreateView(QuestionViewMixin):
    template_name = 'hx/question/answer/answer.html'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        content = self.request.POST.get('content')

        error_messages = []

        if len(content) == 0:
            error_messages.append('A sua resposta não pode estar vazia.')

        if len(content) <= 5:
            error_messages.append('A sua resposta precisa ter mais de 5 carácteres.')

        if len(content) > 986:
            error_messages.append('A sua repsosta não pode ter mais de 986 carácteres.')

        if error_messages:
            return HttpResponse(render_error(error_messages), status=400)

        Answer.objects.create(user=self.request.user, question=self.get_question, content=content)

        context['answers'] = Answer.objects.filter(question=self.get_question).order_by('created')
        context['form'] = AnswerForm()

        return self.render_to_response(context)


class AnswerRenderUpdateView(AnswerMixin):
    template_name = 'hx/question/answer/update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = AnswerForm(instance=self.get_answer)

        return context


class AnswerUpdateView(AnswerMixin):
    template_name = 'hx/question/answer/content.html'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        answer = self.get_answer
        content = request.POST.get('content')
        error_messages = []

        if len(content) == 0:
            error_messages.append('Os detalhes da sua resposta não podem estar vazios.')

        if len(content) <= 5:
            error_messages.append('A sua resposta precisa ter mais de 5 carácteres.')

        if len(content) > 986:
            error_messages.append('A sua repsosta não pode ter mais de 986 carácteres.')

        if error_messages:
            return HttpResponse(render_error(error_messages), status=400)

        answer.content = content
        answer.save()

        return self.render_to_response(context)


class AnswerConfirmDeleteView(AnswerMixin):
    template_name = 'hx/modal/confirm_body.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = context | {
            'confirm_text': 'Você tem certeza que deseja deletar a sua resposta?',
            'post_url': f'/course/answer/delete/{self.get_answer.id}/',
            'target': '#answers',
        }
        return context


class AnswerDeleteView(AnswerMixin):
    template_name = 'hx/question/answer/answer.html'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        question = self.get_answer.question
        answers = Answer.objects.filter(question=question).order_by('updated')
        form = AnswerForm()

        self.get_answer.delete()

        context = {
            'answers': answers,
            'form': form,
            'question': question
        }

        return self.render_to_response(context)
