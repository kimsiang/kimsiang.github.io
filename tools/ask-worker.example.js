/**
 * Optional LLM synthesis for the home-page ask-bar — a Cloudflare Worker.
 *
 *   wrangler secret put ANTHROPIC_API_KEY
 *   wrangler deploy
 *   // then in content/home.html, before ask.js:  <script>window.MUON_ASK_ENDPOINT='https://ask.<you>.workers.dev'</script>
 *
 * Contract: POST {question, lang: 'en'|'zh', contexts: [{n, title, text, url}]}  →  {answer}
 * The model only sees the passages the browser already retrieved, and must cite them as [n].
 */
const ALLOW = ['https://kimsiang.github.io', 'http://127.0.0.1:8765'];
const MODEL = 'claude-haiku-5-5';

export default {
  async fetch(req, env) {
    const origin = req.headers.get('origin') || '';
    const cors = { 'access-control-allow-origin': ALLOW.includes(origin) ? origin : ALLOW[0], 'access-control-allow-headers': 'content-type', 'access-control-allow-methods': 'POST' };
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (req.method !== 'POST') return new Response('POST only', { status: 405, headers: cors });
    const { question, lang, contexts } = await req.json();
    if (!question || !Array.isArray(contexts) || question.length > 400) return new Response('bad request', { status: 400, headers: cors });

    const passages = contexts.slice(0, 6).map((c) => `[${c.n}] ${c.title}\n${String(c.text).slice(0, 1500)}`).join('\n\n');
    const system = `You answer questions about the TDLI Muon Physics Group (Shanghai Jiao Tong University) for visitors of its website.
Use ONLY the numbered passages provided. Cite every claim with its passage number like [2]. If the passages do not answer the question, say so in one sentence and do not guess.
Answer in ${lang === 'zh' ? 'Chinese (简体中文)' : 'English'}, in at most 120 words, plain prose, no headings.`;

    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-api-key': env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model: MODEL, max_tokens: 400, system, messages: [{ role: 'user', content: `Passages:\n\n${passages}\n\nQuestion: ${question}` }] }),
    });
    if (!r.ok) return new Response(JSON.stringify({ error: r.status }), { status: 502, headers: { ...cors, 'content-type': 'application/json' } });
    const j = await r.json();
    const answer = (j.content || []).map((b) => b.text || '').join('').trim();
    return new Response(JSON.stringify({ answer }), { headers: { ...cors, 'content-type': 'application/json', 'cache-control': 'no-store' } });
  },
};
