# Plano de ação — Performance e SEO da FEPI

**Projeto:** `mauriciobtsso/fepi-site`  
**URL avaliada:** `https://fepiaui.org.br/`  
**Dispositivo:** Mobile, Moto G Power emulado, 4G lento  
**Relatório:** 27 de agosto de 2026, 12:50 BRT

## Diagnóstico de partida

O relatório apresenta desempenho 88, acessibilidade 93, práticas recomendadas 96 e SEO 92. O principal espaço de melhoria está no carregamento visual: FCP de 2,7 s e LCP de 3,2 s. Em contrapartida, TBT de 10 ms e CLS de 0,008 indicam que a execução JavaScript e a estabilidade do layout já estão em bom nível e devem ser preservadas.

| Evidência do relatório | Impacto estimado | Tratamento planejado |
|---|---:|---|
| Melhorar entrega de imagens | 57 KiB | Transformações Cloudinary adequadas ao tamanho exibido, `srcset`, `sizes`, `width`, `height` e `decoding` nas páginas públicas prioritárias. |
| JavaScript não utilizado | 69 KiB | Evitar novos scripts globais, manter scripts de página no fim do documento e adiar integrações não críticas quando possível. |
| CSS não utilizado | 18 KiB | Não fazer uma remoção global arriscada nesta rodada; reduzir somente dependências de páginas públicas quando houver evidência clara. |
| Fonte sem `font-display` explícito | 70 ms | Preservar carregamento não bloqueante e documentar a dependência externa; não substituir fontes sem teste visual. |
| Cadeia crítica de rede | 895 ms | Reduzir bytes e dependências de imagens; manter apenas conexões antecipadas que têm uso real. |
| VLibras sem `alt` e com proporção incorreta | Acessibilidade, práticas e SEO | Adicionar semântica ao contêiner de integração e evitar duplicação/alteração do widget externo; validar após inicialização do fornecedor. |
| Miniatura do YouTube com cache curto | 18 KiB | Manter `loading="lazy"` e não transformar o recurso de terceiro; o TTL é controlado pelo YouTube. |

## Implementação segura

A primeira rodada ficará concentrada em templates públicos e em uma otimização equivalente da consulta da home. As alterações não mudam modelos, migrações, URLs, autenticação ou regras editoriais. Imagens acima da dobra recebem prioridade apenas quando são o conteúdo principal; imagens secundárias permanecem lazy. As versões Cloudinary usam `f_auto` e qualidade automática de economia nos tamanhos compatíveis com a área de exibição.

Também será corrigida a sobrescrita de Open Graph dos detalhes de notícia e curso. O layout base expõe o bloco `og_image_tag`, enquanto esses templates usavam um bloco diferente e, portanto, não substituíam de fato a imagem social padrão.

Não será ativada nesta rodada uma política CSP/HSTS nova nem será removido o VLibras, Font Awesome, Google Analytics, YouTube ou Bootstrap de forma ampla. Essas mudanças dependem de validação em produção e podem quebrar integrações ou recursos administrativos.

## Critérios de aceite

A aplicação deve passar `python manage.py check`, toda a suíte de testes existente e `collectstatic`. Os templates devem compilar sem erro e manter URLs, formulários e navegação existentes. A auditoria estática deve confirmar que as imagens públicas prioritárias possuem `alt`, dimensões, `decoding` e carregamento coerentes, e que os detalhes de notícia/curso emitem a tag correta de Open Graph.

Após a publicação, recomenda-se repetir o PageSpeed em celular e computador, comparar FCP/LCP/TBT/CLS e observar o relatório de imagens. A pontuação pode variar por rede, cache, conteúdo editorial e respostas de terceiros; o objetivo técnico desta rodada é reduzir bytes e latência sem sacrificar conteúdo ou funcionalidade.

## Referências técnicas

1. [Chrome for Developers — Optimize Largest Contentful Paint](https://web.dev/articles/optimize-lcp)
2. [Chrome for Developers — Responsive images](https://web.dev/learn/images/responsive-images)
3. [Chrome for Developers — Lazy loading images and iframes](https://web.dev/articles/browser-level-image-lazy-loading)
4. [Google Search Central — Control crawling and indexing](https://developers.google.com/search/docs/crawling-indexing)
