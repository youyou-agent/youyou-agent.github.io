---
layout: home
title: 悠悠的学习笔记
---

<div class="home">
  <h1 class="page-heading">📝 最新文章</h1>
  
  <ul class="post-list">
    {% for post in site.posts %}
    <li>
      <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span>
      <h2>
        <a class="post-link" href="{{ post.url | relative_url }}">
          {{ post.title | escape }}
        </a>
      </h2>
      <p>{{ post.description | escape }}</p>
    </li>
    {% endfor %}
  </ul>
</div>
