<template>
<header>
  <div class="global-menu-button" @click="toggleMenu">
    <img id="menu-toggle" :src="url" aria-hidden="true">
  </div>

  <div id="soft-symbol">
    <span class="renom">ReNom&nbsp;&nbsp;</span>
    <span class="current-page">IMG &gt; {{ currentPage }}</span>
  </div>

</header>
</template>

<script>
export default {
  name: 'AppHeader',
  data: function () {
    return {
      url: require('../../../static/img/han.png')
    }
  },
  computed: {
    currentPage () {
      return this.$store.state.page_name
    }
  },
  methods: {
    toggleMenu: function () {
      this.$store.commit('setNavigationBarShowFlag', {
        flag: !this.$store.state.navigation_bar_shown_flag
      })
    }
  }
}
</script>


<style lang="scss" scoped>
header {

  display: flex;
  position: fixed;
  top:0;
  width: 100%;
  height: $application-header-hight;
  margin: 0;
  padding: 0;

  background-color: $header-color;
  z-index: 999;

  .global-menu-button {
    margin-left: calc(#{$content-top-heder-horizonral-margin}*2);
    line-height: $application-header-hight;
    vertical-align: middle;

    #menu-toggle{
      color: #bbbbbb;
      cursor: pointer;
      vertical-align: middle;
      height:$header-product-name-font-size;
    }
  }

  .help-menu-button {
    margin-left: auto;
    margin-right: calc(#{$content-top-heder-horizonral-margin}*4);
    line-height: $application-header-hight;
    vertical-align: middle;
  }

  #soft-symbol {
    margin: 0;
    text-align: left;
    color: $font-color;

    .renom, .current-page {
      line-height: $application-header-hight;
      vertical-align: middle;
    }
    .renom {
      margin-left: $content-top-heder-horizonral-margin;
      font-family:$header-product-name-font-family;
      font-size: $header-product-name-font-size;
    }

    .current-page {
      font-family:$header-title-font-family;
      font-size: $header-title-font-size;
    }

  }
}
</style>
