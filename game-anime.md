---
layout: default
title: 游戏动漫
permalink: /game-anime/
---

<div class="home">
  <h1 class="page-heading">🎮📺 游戏动漫</h1>
  <p class="post-meta">新游评测、经典回顾、春季新番、动漫推荐——悠悠的 ACG 小窝</p>

  {%- assign game_posts = site.posts | where: "category", "游戏动漫" -%}
  {%- if game_posts.size > 0 -%}
    <ul class="post-list">
      {%- for post in game_posts -%}
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
    <p>暂无游戏动漫文章，悠悠正在努力补番中 🎮</p>
  {%- endif -%}
</div>
