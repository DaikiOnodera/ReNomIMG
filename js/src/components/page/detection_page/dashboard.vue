<template>
  <div id="dashboard">
    <div class="row">
      <div class="col-md-7 col-sm-12">
        <div class="title">
          <div class="title-text">
            Dashboard
          </div>
        </div>
        <div class="content">
          <div class="dashboard-model-summary">
            <div>
              <model-ratio-bar></model-ratio-bar>
            </div>
            <div>
              <running-models></running-models>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-5 col-sm-12">
        <div class="title">
          <div class="title-text">
            Model Map
          </div>
        </div>
        <div class="content">

            <div class="dashboard-model-plot">
              <model-plot></model-plot>
            </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import ModelRatioBar from './dashboard_parts/model_ratio_bar.vue'
import RunningModels from './dashboard_parts/running_models.vue'
import ModelPlot from './dashboard_parts/model_plot.vue'

export default {
  name: 'DashBoard',
  components: {
    'model-ratio-bar': ModelRatioBar,
    'running-models': RunningModels,
    'model-plot': ModelPlot
  }
}
</script>

<style lang="scss" scoped>
#dashboard {

  margin: 0;
  margin-top: $component-margin-top;
  // margin-left: $component-inner-horizontal-margin;

  .title {
    height:$content-top-header-hight;
    background-color: $header-color;
    font-size: $content-top-header-font-size;
    font-family: $content-top-header-font-family;
    color: $font-color;
    .title-text{
      line-height: $content-top-header-hight;
      margin-left: $content-top-heder-horizonral-margin;
    }
  }

  .content {
    display: flex;
    display: -webkit-flex;
    margin-top: $content-top-margin;
    height: $content-dashboard-height;
    background-color: $content-bg-color;
    border: 1px solid $content-border-color;
    padding: $content-top-padding $content-horizontal-padding $content-bottom-padding;


    .dashboard-model-summary {
      width: 100%;
      #model-ratio-bar {
        height: 40%;
      }
      #running-models {
        height: 60%;
      }
    }

    .dashboard-model-plot {
      width: 100%;
      height: 100%;
      margin-left: 0;
    }
  }
}
</style>
