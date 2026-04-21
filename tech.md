---
layout: default
title: 技术分享
permalink: /tech/
---

<div class="home">
  <h1 class="page-heading">🔧 技术分享</h1>
  <p class="post-meta">AI Agent 开发、存储行业分析、系统运维、游戏开发等技术文章</p>

  {%- assign tech_posts = site.posts | where: "category", "技术分享" -%}
  {%- if tech_posts.size > 0 -%}
    <ul class="post-list">
      {%- for post in tech_posts -%}
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
    <p>暂无技术文章</p>
  {%- endif -%}
</div>
