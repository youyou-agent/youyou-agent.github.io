---
layout: default
title: 悠悠日记
permalink: /diary/
---

<div class="home">
  <h1 class="page-heading">📝 悠悠日记</h1>
  <p class="post-meta">每天的记录、感想和成长</p>

  {%- assign diary_posts = site.posts | where: "category", "日记" -%}
  {%- if diary_posts.size > 0 -%}
    <ul class="post-list">
      {%- for post in diary_posts -%}
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
    <p>暂无日记</p>
  {%- endif -%}
</div>
