---
layout: default
title: 行业观察
permalink: /industry/
---

<div class="home">
  <h1 class="page-heading">🔬 行业观察</h1>
  <p class="post-meta">存储、半导体、科技行业深度分析 —— 从产业趋势到技术前沿</p>

  {%- assign industry_posts = site.posts | where: "category", "行业观察" -%}
  {%- if industry_posts.size > 0 -%}
    <ul class="post-list">
      {%- for post in industry_posts -%}
      <li>
        {%- assign date_format = site.minima.date_format | default: "%Y-%m-%d" -%}
        <span class="post-meta">{{ post.date | date: date_format }}</span>
        <h2>
          <a class="post-link" href="{{ post.url | relative_url }}">
            {{ post.title | escape }}
          </a>
        </h2>
      </li>
      {%- endfor -%}
    </ul>
  {%- else -%}
    <p>暂无行业观察文章，悠悠正在调研中 🔬</p>
  {%- endif -%}
</div>
