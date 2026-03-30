---
layout: home
title: 悠悠的学习笔记
---

<div class="home">
  <p class="description">
    AI 技术 · 存储领域 · 日常思考
  </p>
  
  <h2 class="post-list-heading">📝 最新文章</h2>
  <ul class="post-list">
    {% for post in site.posts %}
    <li>
      <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span>
      <h3>
        <a class="post-link" href="{{ post.url | relative_url }}">
          {{ post.title | escape }}
        </a>
      </h3>
      {% if post.description %}
      <p class="post-description">{{ post.description }}</p>
      {% endif %}
      {% if post.tags.size > 0 %}
      <div class="post-tags">
        {% for tag in post.tags %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
      </div>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
</div>
