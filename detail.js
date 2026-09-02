const L={en:{dashboard:"PMO Dashboard",details:"Project details",code:"Project code",deptCode:"Department code",completion:"Completion rate",implementation:"Implementation rate",operation:"Operation rate",actual:"Actual",planned:"Planned",actualCompletion:"Actual completion",plannedCompletion:"Planned completion",actualImplementation:"Actual implementation",plannedImplementation:"Planned implementation",actualOperation:"Actual operation",plannedOperation:"Planned operation",achievements:"Achievements",next:"Next steps",challenges:"Challenges & risks",support:"Support needed",comments:"Comments",commentsPlaceholder:"Add project comments…",saveComments:"Save comments",commentsSaved:"Comments saved",saving:"Saving…",loading:"Loading project…",error:"Project could not be loaded.",edit:"Edit project",editing:"Edit project information",cancel:"Cancel",update:"Update project"},ar:{dashboard:"لوحة مكتب إدارة المشاريع",details:"تفاصيل المشروع",code:"رمز المشروع",deptCode:"رمز الإدارة",completion:"نسبة الإنجاز",implementation:"نسبة التنفيذ",operation:"نسبة التشغيل",actual:"الفعلي",planned:"المخطط",actualCompletion:"الإنجاز الفعلي",plannedCompletion:"الإنجاز المخطط",actualImplementation:"التنفيذ الفعلي",plannedImplementation:"التنفيذ المخطط",actualOperation:"التشغيل الفعلي",plannedOperation:"التشغيل المخطط",achievements:"الإنجازات",next:"الخطوات القادمة",challenges:"التحديات والمخاطر",support:"الدعم المطلوب",comments:"التعليقات",commentsPlaceholder:"أضف تعليقات المشروع…",saveComments:"حفظ التعليقات",commentsSaved:"تم حفظ التعليقات",saving:"جارٍ الحفظ…",loading:"جارٍ تحميل المشروع…",error:"تعذر تحميل المشروع.",edit:"تعديل المشروع",editing:"تعديل بيانات المشروع",cancel:"إلغاء",update:"تحديث المشروع"}};

const q=new URLSearchParams(location.search);
let lang=q.get("lang")==="ar"?"ar":"en",project;
const $=s=>document.querySelector(s),local=f=>project[f+(lang==="en"?"En":"Ar")]||"—";

function installManagerFields(){const codes=$(".project-codes");
codes.insertAdjacentHTML("beforeend",'<details class="manager-disclosure"><summary><span id="managerMoreLabel">More</span></summary><div class="manager-facts"><div><span id="managerNameLabel">Project manager name</span><strong id="projectManagerName"></strong></div><div><span id="managerEmailLabel">Project manager email</span><strong id="projectManagerEmail"></strong></div></div></details>');
const firstFieldset=$("#editForm fieldset");
firstFieldset.insertAdjacentHTML("beforebegin",'<label><span id="editManagerNameLabel">Project manager name</span><input name="projectManagerName"></label><label><span id="editManagerEmailLabel">Project manager email</span><input type="email" name="projectManagerEmail"></label>')}
installManagerFields();

function show(){const t=L[lang],managerName=lang==="en"?"Project manager name":"اسم مدير المشروع",managerEmail=lang==="en"?"Project manager email":"البريد الإلكتروني لمدير المشروع";
document.documentElement.lang=lang;
document.documentElement.dir=lang==="ar"?"rtl":"ltr";
$("#brandTitle").textContent=t.dashboard;
$("#langBtn").textContent=lang==="en"?"العربية":"English";
$("#editBtn").textContent="✎ "+t.edit;
$("#editMode").textContent=t.editing;
$("#editCancel").textContent=t.cancel;
$("#updateBtn").textContent=t.update;
$("#commentsLabel").textContent=t.comments;
$("#comments").placeholder=t.commentsPlaceholder;
$("#saveComments").textContent=t.saveComments;
$("#managerNameLabel").textContent=$("#editManagerNameLabel").textContent=managerName;
$("#managerEmailLabel").textContent=$("#editManagerEmailLabel").textContent=managerEmail;
$("#managerMoreLabel").textContent=lang==="en"?"More":"المزيد";
[["detailsLabel","details"],["codeLabel","code"],["deptCodeLabel","deptCode"],["achievementsLabel","achievements"],["nextLabel","next"],["challengesLabel","challenges"],["supportLabel","support"],["editCodeLabel","code"],["editDeptCodeLabel","deptCode"]].forEach(([id,k])=>$("#"+id).textContent=t[k]);
["actualCompletion","plannedCompletion","actualImplementation","plannedImplementation","actualOperation","plannedOperation"].forEach(k=>$("#edit"+k[0].toUpperCase()+k.slice(1)+"Label").textContent=t[k]);
document.querySelectorAll(".actualLabel").forEach(e=>e.textContent=t.actual);
document.querySelectorAll(".plannedLabel").forEach(e=>e.textContent=t.planned);
showComparison("completion",project.actualCompletionRate,project.plannedCompletionRate);
showComparison("implementation",project.actualImplementationRate,project.plannedImplementationRate);
showComparison("operation",project.actualOperationRate,project.plannedOperationRate);
$("#completionCategory").textContent=t.completion;
$("#implementationCategory").textContent=t.implementation;
$("#operationCategory").textContent=t.operation;
$("#projectName").textContent=local("projectName");
$("#departmentName").textContent=local("departmentName");
$("#projectCode").textContent=project.projectCode;
$("#departmentCode").textContent=project.departmentCode;
$("#projectManagerName").textContent=project.projectManagerName||"—";
$("#projectManagerEmail").textContent=project.projectManagerEmail||"—";
["achievements","nextSteps","challengesRisks","supportNeeded"].forEach(f=>$("#"+f).textContent=local(f));
$("#comments").value=project.comments||"";
$("#detailState").classList.add("hidden");
$("#detailContent").classList.remove("hidden")}
function showComparison(category,actual,planned){$("#actual"+category[0].toUpperCase()+category.slice(1)+"Rate").textContent=actual+"%";
$("#planned"+category[0].toUpperCase()+category.slice(1)+"Rate").textContent=planned+"%";
$("#actual"+category[0].toUpperCase()+category.slice(1)+"Circle").style.setProperty("--rate",actual*3.6+"deg");
const row=$("#"+category+"Comparison");
row.classList.remove("rate-red","rate-orange","rate-green");
row.classList.add(actual<50?"rate-red":actual<80?"rate-orange":"rate-green")}
function load(){fetch("/api/projects").then(r=>r.json()).then(d=>{project=d.projects.find(p=>String(p.id)===q.get("id"));
if(!project)throw Error();
show()}).catch(()=>$("#detailState").textContent=L[lang].error)}
function openEdit(){for(const[k,v]of Object.entries(project))if($("#editForm").elements[k])$("#editForm").elements[k].value=v;
["actualCompletion","plannedCompletion","actualImplementation","plannedImplementation","actualOperation","plannedOperation"].forEach(k=>$("#edit"+k[0].toUpperCase()+k.slice(1)+"Value").textContent=project[k+"Rate"]+"%");
$("#editTitle").textContent=local("projectName");
$("#editOverlay").classList.remove("hidden")}
function closeEdit(){$("#editOverlay").classList.add("hidden")}$("#editForm").onsubmit=async e=>{e.preventDefault();
const body=Object.fromEntries(new FormData(e.target));
["actualCompletionRate","plannedCompletionRate","actualImplementationRate","plannedImplementationRate","actualOperationRate","plannedOperationRate"].forEach(k=>body[k]=Number(body[k]));
body.comments=project.comments||"";
const r=await fetch(`/api/projects/${project.id}`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
if(r.ok){project=(await r.json()).project;
closeEdit();
show()}};
$("#saveComments").onclick=async()=>{const button=$("#saveComments"),status=$("#commentsStatus");
button.disabled=true;
button.textContent=L[lang].saving;
status.textContent="";
const body={...project,comments:$("#comments").value};
delete body.id;
const r=await fetch(`/api/projects/${project.id}`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
if(r.ok){project=(await r.json()).project;
status.textContent=L[lang].commentsSaved}button.disabled=false;
button.textContent=L[lang].saveComments};
$("#comments").oninput=()=>$("#commentsStatus").textContent="";
$("#langBtn").onclick=()=>{lang=lang==="en"?"ar":"en";
show()};
$("#editBtn").onclick=openEdit;
$("#editClose").onclick=$("#editCancel").onclick=closeEdit;
["actualCompletion","plannedCompletion","actualImplementation","plannedImplementation","actualOperation","plannedOperation"].forEach(k=>$("#editForm").elements[k+"Rate"].oninput=e=>$("#edit"+k[0].toUpperCase()+k.slice(1)+"Value").textContent=e.target.value+"%");
load();
