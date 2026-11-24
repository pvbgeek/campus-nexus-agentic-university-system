"use strict";
const workspace = document.querySelector("#workspace");
let user = null;
const money = cents => new Intl.NumberFormat("en-US", {style:"currency",currency:"USD"}).format(cents/100);
const node = (tag, text, cls) => { const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(cls)e.className=cls; return e; };
const toast = text => { const e=document.querySelector("#toast"); e.textContent=text; e.style.display="block"; setTimeout(()=>e.style.display="none",6000); };
async function api(path, method="GET", body) {
  const headers={}; if(body!==undefined)headers["Content-Type"]="application/json";
  if(method!=="GET" && user)headers["X-CSRF-Token"]=user.csrf;
  const response=await fetch("/api"+path,{method,headers,credentials:"same-origin",body:body===undefined?undefined:JSON.stringify(body)});
  const data=await response.json().catch(()=>({detail:"Server returned an unexpected response"}));
  if(!response.ok)throw new Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail));
  return data;
}
function clear(title, description) {
  workspace.replaceChildren(); workspace.setAttribute("aria-busy","false");
  const intro=node("div",undefined,"intro"), inner=node("div");
  inner.append(node("h1",title)); if(description)inner.append(node("p",description));
  intro.append(inner); workspace.append(intro);
}
function button(text, handler, cls="btn") {
  const b=node("button",text,cls); b.type="button";
  b.addEventListener("click",async()=>{b.disabled=true;try{await handler();}catch(e){toast(e.message);}finally{b.disabled=false;}});
  return b;
}
function field(form,label,type="text",value="") {
  const wrap=node("div",undefined,"field"), id="field-"+crypto.randomUUID();
  const l=node("label",label); l.htmlFor=id;
  const input=node(type==="textarea"?"textarea":"input"); input.id=id;
  if(type!=="textarea")input.type=type;
  input.value=value; input.required=true; wrap.append(l,input);form.append(wrap);return input;
}
function card(title) { const c=node("section",undefined,"panel support-card");c.append(node("h2",title));return c; }
function link(text,href) {const a=node("a",text,"btn secondary");a.href=href;return a;}
function showLogin() {
  clear("Sign in to Campus Nexus", "Use a local demo identity. Credentials are in data/demo-login.txt on the computer running the server.");
  const form=node("form",undefined,"panel support-login");
  const username=field(form,"Username"),password=field(form,"Password","password");
  username.autocomplete="username";password.autocomplete="current-password";
  const error=node("p","","support-error");error.setAttribute("role","alert");
  const submit=node("button","Sign in","btn");submit.type="submit";form.append(error,submit);
  form.addEventListener("submit",async e=>{e.preventDefault();submit.disabled=true;try{user=await api("/login","POST",{username:username.value,password:password.value});password.value="";location.href=user.role==="staff"?"staff.html":"orders.html";}catch(err){error.textContent=err.message;}finally{submit.disabled=false;}});
  form.append(button("Create customer account", showSignup, "btn secondary"));
  workspace.append(form);
}
function showSignup() {
  clear("Create a customer account", "Use a demo username. Your account comes with one synthetic order.");
  const form = node("form", undefined, "panel support-login");
  const username = field(form, "Username");
  const password = field(form, "Password", "password");
  username.autocomplete = "username";
  password.autocomplete = "new-password";
  password.minLength = 12;
  const error = node("p", "", "support-error");
  error.setAttribute("role", "alert");
  const submit = node("button", "Create account", "btn");
  submit.type = "submit";
  form.append(error, submit, button("Back to sign in", showLogin, "btn secondary"));
  form.addEventListener("submit", async event => {
    event.preventDefault();
    submit.disabled = true;
    try {
      await api("/signup", "POST", {username: username.value, password: password.value});
      showLogin();
      toast("Account created. Sign in with your new credentials.");
    } catch (err) {
      error.textContent = err.message;
    } finally {
      submit.disabled = false;
    }
  });
  workspace.append(form);
}
async function renderOrders() {
  const data=await api("/orders");
  clear("My orders", "These synthetic records belong to your signed-in customer account.");
  workspace.append(node("p", "Mock account credits: "+money(data.account.balance)+" · "+data.account.destination,"notice"));
  for(const order of data.orders){const c=card("Order #"+order.id);
    c.append(node("p","Order total: "+money(order.total)+" · Remaining refundable: "+money(order.remaining_cents)));
    if(order.supervisor_denied)c.append(node("p","Supervisor denied refunds for this order.","notice red"));
    c.append(link("Request a refund","refund.html?order="+encodeURIComponent(order.id)));workspace.append(c);}
  workspace.append(node("p","This progress build checks reason category, order balance and authority. Staff must verify supporting evidence before execution. The gateway checks the synthetic delivery date against the 30 day window.","notice"));
}
async function renderRefund() {
  const data=await api("/orders"),requested=new URLSearchParams(location.search).get("order");
  const order=data.orders.find(o=>o.id===requested)||data.orders[0];
  clear("Request a refund", "Submitting opens a case. A refund is credited only after staff processing and the independent authorization check.");
  if(!order){workspace.append(node("p","No orders found."));return;}
  const form=node("form",undefined,"panel");
  const select=node("select");select.id="refund-order";const label=node("label","Order");label.htmlFor=select.id;
  for(const o of data.orders){const opt=node("option",o.id+" · "+money(o.remaining_cents)+" remaining");opt.value=o.id;opt.selected=o.id===order.id;select.append(opt);}
  form.append(label,select);
  const amount=field(form,"Refund amount (USD)","text",(Math.min(order.remaining_cents,6400)/100).toFixed(2));amount.inputMode="decimal";
  const reason=node("select");reason.id="refund-reason";const reasonLabel=node("label","Reason");reasonLabel.htmlFor=reason.id;
  for(const [value,text] of [["damaged","Item arrived damaged"],["wrong_item","Incorrect item"],["duplicate_charge","Duplicate charge"]]){const opt=node("option",text);opt.value=value;reason.append(opt);}form.append(reasonLabel,reason);
  const details=field(form,"What happened? Do not include bank details.","textarea");details.maxLength=2000;
  const error=node("p","","support-error");error.setAttribute("role","alert");
  const submit=node("button","Submit request","btn");submit.type="submit";form.append(error,submit);
  let requestKey=crypto.randomUUID(),lastPayload="";
  form.addEventListener("submit",async e=>{e.preventDefault();submit.disabled=true;error.textContent="";
    try{const raw=amount.value.trim();if(!/^\d{1,6}(\.\d{1,2})?$/.test(raw))throw new Error("Enter a positive USD amount with at most two decimal places.");
      const [whole,fraction=""]=raw.split("."),cents=Number(whole)*100+Number(fraction.padEnd(2,"0"));if(cents<=0)throw new Error("Amount must be positive.");
      const payload={order_id:select.value,amount_cents:cents,reason:reason.value,details:details.value};
      const signature=JSON.stringify(payload);if(lastPayload && signature!==lastPayload)requestKey=crypto.randomUUID();lastPayload=signature;
      const result=await api("/cases","POST",{...payload,request_key:requestKey});
      clear("Request received", "Case #"+result.case_id+" was saved. This is not a refund approval.");
      workspace.append(node("p","Acknowledgement saved to the case’s mock inbox. No external email was sent.","notice"),link("Track my case","cases.html?case="+encodeURIComponent(result.case_id)));
    }catch(err){error.textContent=err.message;}finally{submit.disabled=false;}});workspace.append(form);
}
async function addCaseDetails(container, id) {
  const data=await api("/cases/"+encodeURIComponent(id));
  container.append(node("p",data.case.details,"message support-detail"));
  for(const run of data.runs||[]){const section=node("details");section.append(node("summary","Agent run "+run.id+" · "+run.status),node("pre",JSON.stringify(run.state,null,2),"support-json"));container.append(section);}
  for(const message of data.messages){const m=node("div",undefined,"message");m.append(node("strong",message.kind+" · Mock inbox"),node("p",message.body,"support-detail"),node("small",message.created));container.append(m);}
  if (user?.role === "customer") {
    const form = node("form", undefined, "panel");
    const input = field(form, "Add a follow-up", "textarea");
    input.maxLength = 2000;
    const submit = node("button", "Send follow-up", "btn");
    submit.type = "submit";
    const feedback = node("p");
    feedback.setAttribute("role", "status");
    form.append(submit, feedback);
    form.addEventListener("submit", async event => {
      event.preventDefault();
      submit.disabled = true;
      try {
        await api("/cases/" + encodeURIComponent(id) + "/messages",
                  "POST", {text: input.value});
        container.replaceChildren();
        await addCaseDetails(container, id);
        container.querySelector("textarea")?.focus();
        const status = container.querySelector("[role=status]");
        if (status) status.textContent = "Follow-up saved.";
      } catch (error) {
        feedback.textContent = error.message;
      } finally {
        submit.disabled = false;
      }
    });
    container.append(form);
  }
}
async function renderCases(staff=false) {
  if(staff && user.role!=="staff")throw new Error("Staff access required.");
  const cases=await api("/cases");clear(staff?"Staff workspace":"My cases",staff?"Verify evidence, run the five Groq agents, or record a supervisor decision. The independent gateway rechecks limits at execution.":"View saved requests, decisions and mock inbox messages.");
  if(!cases.length)workspace.append(node("p","No cases yet.","notice"));
  for(const c of cases){const panel=card("Case #"+c.id);
    panel.append(node("p","Order "+c.order_id+" · "+money(c.amount)+" · "+c.reason),node("p","Status: "+c.status+" · Reason: "+c.decision_reason,"notice"));
    panel.append(button("View case and messages",async()=>{const detail=node("div");await addCaseDetails(detail,c.id);panel.append(detail);},"btn secondary"));
    if(!staff){panel.append(button("Ask agents to review",async()=>{if(!confirm("Run a live agent review? It may take a minute. Evidence must still be verified by staff before execution."))return;const result=await api("/cases/"+encodeURIComponent(c.id)+"/review","POST",{});toast(result.execution.status+": "+result.execution.reason);await renderCases(false);},"btn secondary"));}
    if(staff){const note=field(panel,"Staff evidence assessment or decision reason","textarea");note.required=false;
      const actions=node("div",undefined,"support-actions");
      actions.append(button("Process refund",async()=>{if(!confirm("Run the five Groq agents? This can take a minute and may credit a mock account after authorization."))return;const r=await api("/cases/"+encodeURIComponent(c.id)+"/process","POST",{});toast(r.status+" · "+r.execution.status+": "+r.execution.reason);await renderCases(true);}));
      for(const decision of ["verify","deny","escalate"])actions.append(button(decision==="verify"?"Verify evidence":decision==="deny"?"Deny request":"Escalate",async()=>{if(!note.value.trim())throw new Error("Record a decision reason first.");await api("/cases/"+encodeURIComponent(c.id)+"/decision","POST",{decision,note:note.value});await renderCases(true);},"btn secondary"));
      panel.append(actions);}
    workspace.append(panel);}
}
async function renderReports() {
  const data=await api("/reports");clear("Reports and oversight", "Current persisted ledger. Every amount is synthetic; no real payment provider is connected.");
  const summary=card("Week beginning "+data.week_start_utc+" UTC");
  summary.append(node("p","Executed: "+money(data.weekly_used_cents)+" / $500.00 · Remaining: "+money(data.weekly_remaining_cents)),node("p","Refund authority: "+(data.active?"Active":"Revoked")));
  const note=field(summary,"Reason for changing authority","textarea");note.required=false;
  summary.append(button(data.active?"Revoke refund authority":"Restore refund authority",async()=>{if(!note.value.trim())throw new Error("Record a reason first.");await api("/authority","POST",{active:!data.active,note:note.value});await renderReports();},"btn secondary"));workspace.append(summary);
  for(const c of data.cases){const panel=card(c.id);panel.append(node("p",money(c.amount)+" requested · "+(c.refund_id?"executed":c.status)),node("p",c.decision_reason));workspace.append(panel);}
  const auditPanel=card("Audit records");auditPanel.append(button("Load audit records",async()=>{const records=await api("/audit");const pre=node("pre",JSON.stringify(records,null,2),"support-json");auditPanel.append(pre);},"btn secondary"));workspace.append(auditPanel);
}
async function start(){
  try{user=await api("/me");}catch(e){showLogin();return;}
  document.querySelectorAll("[data-staff]").forEach(e=>e.hidden=user.role!=="staff");
  const signout=document.querySelector("#sign-out");signout.hidden=false;signout.addEventListener("click",async()=>{try{await api("/logout","POST",{});location.href="index.html";}catch(e){toast(e.message);}});
  const page=location.pathname.split("/").pop();
  try{if(page==="index.html"||!page)location.replace(user.role==="staff"?"staff.html":"orders.html");
    else if(page==="orders.html")await renderOrders();else if(page==="refund.html")await renderRefund();
    else if(page==="cases.html")await renderCases();else if(page==="staff.html")await renderCases(true);
    else if(page==="reports.html")await renderReports();
  }catch(e){clear("Unable to load this view",e.message);workspace.append(link("Return to sign in","index.html"));}
}
start();
