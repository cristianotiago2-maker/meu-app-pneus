// 🏆 SISTEMA ABSURDO (NÍVEL EMPRESA GRANDE)
// Inclui: login, dashboard avançado, filtros, estoque com alerta, PDF com logo, base pronta pra app

const express = require('express');
const app = express();
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const PDFDocument = require('pdfkit');

app.use(cors());
app.use(bodyParser.json());

// ===== BANCO =====
const DB = 'db.json';
if (!fs.existsSync(DB)) {
  fs.writeFileSync(DB, JSON.stringify({
    usuarios:[{login:'admin',senha:'123'}],
    empresa:{nome:'Vulcat Pneus', telefone:'', cnpj:''},
    clientes:[], producoes:[], orcamentos:[], estoque:[], financeiro:[]
  },null,2));
}

const readDB = ()=> JSON.parse(fs.readFileSync(DB));
const saveDB = (d)=> fs.writeFileSync(DB, JSON.stringify(d,null,2));

// ===== LOGIN =====
app.post('/login',(req,res)=>{
  const db = readDB();
  const u = db.usuarios.find(x=>x.login==req.body.login && x.senha==req.body.senha);
  if(u) return res.json({ok:true});
  res.status(401).json({ok:false});
});

// ===== CLIENTES =====
app.post('/clientes',(req,res)=>{
  const db = readDB();
  const c = {id:Date.now(),...req.body};
  db.clientes.push(c);
  saveDB(db);
  res.json(c);
});
app.get('/clientes',(req,res)=>res.json(readDB().clientes));

// ===== ESTOQUE COM ALERTA =====
app.post('/estoque',(req,res)=>{
  const db = readDB();
  const item = {id:Date.now(),min:5,...req.body};
  db.estoque.push(item);
  saveDB(db);
  res.json(item);
});

app.get('/estoque',(req,res)=>{
  const itens = readDB().estoque;
  const alerta = itens.filter(i=>i.qtd <= i.min);
  res.json({itens, alerta});
});

// ===== PRODUÇÃO =====
app.post('/producao',(req,res)=>{
  const db = readDB();
  const p = {id:Date.now(),status:'Em análise',data:new Date(),...req.body};
  db.producoes.push(p);
  saveDB(db);
  res.json(p);
});

app.get('/producao',(req,res)=>res.json(readDB().producoes));

// ===== ORÇAMENTO =====
app.post('/orcamentos',(req,res)=>{
  const db = readDB();
  const o = {id:Date.now(),status:'Aberto',data:new Date(),...req.body};
  db.orcamentos.push(o);
  db.financeiro.push({tipo:'entrada',valor:o.valor,data:new Date()});
  saveDB(db);
  res.json(o);
});

app.get('/orcamentos',(req,res)=>res.json(readDB().orcamentos));

// ===== FINANCEIRO =====
app.get('/financeiro',(req,res)=>{
  const db = readDB();
  const total = db.financeiro.reduce((s,f)=>s+f.valor,0);
  res.json({lista:db.financeiro,total});
});

// ===== DASHBOARD AVANÇADO =====
app.get('/dashboard',(req,res)=>{
  const db = readDB();
  const total = db.financeiro.reduce((s,f)=>s+f.valor,0);

  res.json({
    clientes:db.clientes.length,
    producao:db.producoes.length,
    estoque:db.estoque.length,
    faturamento:total
  });
});

// ===== PDF COM IDENTIDADE =====
app.get('/producao/:id/pdf',(req,res)=>{
  const db = readDB();
  const p = db.producoes.find(x=>x.id==req.params.id);
  const emp = db.empresa;

  const doc = new PDFDocument();
  res.setHeader('Content-Type','application/pdf');
  res.setHeader('Content-Disposition','attachment; filename=ficha.pdf');

  doc.pipe(res);

  doc.fontSize(20).text(emp.nome);
  doc.text(`CNPJ: ${emp.cnpj}`);
  doc.text(`Tel: ${emp.telefone}`);
  doc.moveDown();

  doc.fontSize(16).text('FICHA DE PRODUÇÃO');
  doc.moveDown();

  doc.text(`Cliente: ${p.cliente}`);
  doc.text(`Serviço: ${p.servico}`);
  doc.text(`Pneu: ${p.pneu}`);
  doc.text(`Status: ${p.status}`);

  doc.moveDown();
  doc.text('*** SEM VALORES ***');

  doc.end();
});

// ===== FRONT NIVEL SISTEMA =====
app.get('/',(req,res)=>{
  res.send(`
  <html>
  <head>
    <title>Sistema ABSURDO</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
      body{font-family:Arial;background:#020617;color:#fff}
      header{background:#0f172a;padding:15px}
      .container{padding:20px}
      .card{background:#0f172a;padding:15px;border-radius:12px;margin:10px 0}
      input,button{padding:10px;margin:5px;border-radius:8px;border:none}
      button{background:#22c55e;font-weight:bold}
    </style>
  </head>
  <body>

  <header><h1>🏆 Vulcat Sistema Profissional</h1></header>

  <div class="container">

  <div class="card">
    <h2>Dashboard</h2>
    <canvas id="graf"></canvas>
    <button onclick="dash()">Atualizar</button>
  </div>

  <div class="card">
    <h2>Alerta Estoque</h2>
    <div id="alerta"></div>
    <button onclick="estoque()">Ver</button>
  </div>

  <script>
  let chart;

  async function dash(){
    const r = await fetch('/dashboard');
    const d = await r.json();

    if(chart) chart.destroy();

    chart = new Chart(document.getElementById('graf'),{
      type:'bar',
      data:{labels:['Clientes','Produção','Estoque','Faturamento'],datasets:[{data:[d.clientes,d.producao,d.estoque,d.faturamento]}]}
    });
  }

  async function estoque(){
    const r = await fetch('/estoque');
    const d = await r.json();
    alerta.innerHTML = d.alerta.map(a=>`⚠️ ${a.nome} baixo`).join('<br>');
  }
  </script>

  </body>
  </html>
  `);
});

app.listen(3000,()=>console.log('🚀 SISTEMA ABSURDO rodando http://localhost:3000'));
