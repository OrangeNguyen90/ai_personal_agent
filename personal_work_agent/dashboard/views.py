import uuid
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from agent.core import PersonalAgent
from config import WORKSPACE
from memory.store import initialize, connect, add_task, complete_task, remember
from .models import ChatMessage, UploadedDocument
from .forms import DocumentForm

@login_required
def home(request):
    initialize()
    with connect() as db:
        total = db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        pending = db.execute("SELECT COUNT(*) FROM tasks WHERE status='todo'").fetchone()[0]
        mem = db.execute('SELECT COUNT(*) FROM memories').fetchone()[0]
    return render(request,'dashboard/home.html',{'total':total,'pending':pending,'memory_count':mem,'documents_count':UploadedDocument.objects.count()})

@login_required
@require_http_methods(['GET','POST'])
def chat(request):
    if request.method == 'POST':
        question = request.POST.get('question','').strip()[:4000]
        if question:
            history = list(ChatMessage.objects.filter(user=request.user).order_by('-id')[:20])[::-1]
            agent = PersonalAgent()
            agent.messages.extend({'role':m.role,'content':m.content} for m in history)
            try:
                answer = agent.chat(question)
            except Exception as exc:
                answer = 'Không thể kết nối Ollama hoặc xử lý yêu cầu. Hãy kiểm tra ollama list, model và dịch vụ Ollama.'
            ChatMessage.objects.create(user=request.user,role='user',content=question)
            ChatMessage.objects.create(user=request.user,role='assistant',content=answer)
        return redirect('chat')
    history = ChatMessage.objects.filter(user=request.user).order_by('-id')[:50]
    return render(request,'dashboard/chat.html',{'history':list(history)[::-1]})

@login_required
@require_http_methods(['GET','POST'])
def tasks(request):
    initialize()
    if request.method == 'POST':
        action=request.POST.get('action')
        if action=='add':
            title=request.POST.get('title','').strip()[:250]
            if title: add_task(title)
        elif action=='complete':
            try: complete_task(int(request.POST.get('task_id','')))
            except (TypeError,ValueError): messages.error(request,'ID không hợp lệ')
        return redirect('tasks')
    with connect() as db:
        rows=db.execute('SELECT id,title,status,created FROM tasks ORDER BY id DESC LIMIT 200').fetchall()
    return render(request,'dashboard/tasks.html',{'tasks':rows})

@login_required
@require_http_methods(['GET','POST'])
def documents(request):
    WORKSPACE.mkdir(parents=True,exist_ok=True)
    if request.method=='POST':
        form=DocumentForm(request.POST,request.FILES)
        if form.is_valid():
            f=form.cleaned_data['file']
            ext=Path(f.name).suffix.lower()
            if ext not in {'.pdf','.docx','.xlsx','.txt','.md','.csv','.json','.py'}:
                messages.error(request,'Định dạng không được hỗ trợ')
            elif f.size>10_000_000:
                messages.error(request,'File vượt quá 10 MB')
            else:
                stored=f'{uuid.uuid4().hex}{ext}'
                path=WORKSPACE/stored
                with path.open('wb') as output:
                    for chunk in f.chunks(): output.write(chunk)
                UploadedDocument.objects.create(user=request.user,filename=Path(f.name).name[:255],stored_name=stored)
                messages.success(request,'Đã tải lên. Trong chat, yêu cầu đọc file: '+stored)
                return redirect('documents')
    else: form=DocumentForm()
    docs=UploadedDocument.objects.filter(user=request.user)
    return render(request,'dashboard/documents.html',{'form':form,'documents':docs})

@login_required
@require_http_methods(['GET','POST'])
def memories(request):
    initialize()
    if request.method=='POST':
        action=request.POST.get('action')
        if action=='add':
            content=request.POST.get('content','').strip()[:2000]
            if content: remember(content)
        elif action=='delete':
            try:
                item_id=int(request.POST.get('memory_id',''))
                with connect() as db: db.execute('DELETE FROM memories WHERE id=?',(item_id,))
            except (TypeError,ValueError): messages.error(request,'ID không hợp lệ')
        return redirect('memories')
    with connect() as db:
        rows=db.execute('SELECT id,content,created FROM memories ORDER BY id DESC LIMIT 200').fetchall()
    return render(request,'dashboard/memories.html',{'memories':rows})
