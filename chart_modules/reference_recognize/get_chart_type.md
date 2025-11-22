Given the following image of a chart, identify which chart type it most closely resembles from the chart taxonomy below.

Please return:
1. A ranked list (from most likely to least) of the **major chart category** (e.g., "Bar Chart", "Line & Area Chart", etc.) that the image could belong to.
2. For each top-ranked major category, return the **most likely specific chart type(s)**.

**Response format (strict JSON):**
```json
{
  "major_categories": [
    {
      "category": "Bar Charts",
      "candidates": [
        "vertical_group_bar_chart",
        "vertical_bar_chart_with_circle"
      ]
    },
    {
      "category": "Line & Area Charts",
      "candidates": [
        "line_graph"
      ]
    },
    {
      "category": "Specialized Charts",
      "candidates": [
        "dumbbell_plot"
      ]
    }
  ]
}
```

Here is the taxonomy:
---
### 1. Bar Charts
* `vertical_bar_chart`: Vertical Bar Chart
* `vertical_group_bar_chart`: Vertical Grouped Bar Chart
* `horizontal_stacked_bar_chart`: Horizontal Stacked Bar Chart
* `horizontal_group_bar_chart`: Horizontal Grouped Bar Chart
* `circular_bar_chart`: Circular Bar Chart
* `circular_stacked_bar_chart`: Circular Stacked Bar Chart
* `circular_grouped_bar_chart`: Circular Grouped Bar Chart
* `radial_bar_chart`: Radial Bar Chart
* `radial_stacked_bar_chart`: Radial Stacked Bar Chart
* `radial_grouped_bar_chart`: Radial Grouped Bar Chart
* `vertical_bar_chart_with_circle`: Vertical Bar Chart with Circles
* `horizontal_bar_chart_with_circle`: Horizontal Bar Chart with Circles
### 2. Line & Area Charts
* `line_graph`: Line Graph
* `spline_graph`: Spline Curve
* `stepped_line_graph`: Stepped Line Graph
* `slope_chart`: Slope Chart
* `area_chart`: Area Chart
* `spline_area_chart`: Spline Area Chart
* `layered_area_chart`: Layered Area Chart
* `stacked_area_chart`: Stacked Area Chart
### 3. Pie & Donut Charts
* `pie_chart`: Pie Chart
* `donut_chart`: Donut Chart
* `semicircle_pie_chart`: Semi-circle Pie Chart
* `semicircle_donut_chart`: Semi-circle Donut Chart
* `rose_chart`: Rose Chart
### 4. Scatter & Bubble Charts
* `scatterplot`: Scatter Plot
* `grouped_scatterplot`: Grouped Scatter Plot
* `bubble_chart`: Bubble Chart
### 5. Specialized Charts
* `dumbbell_plot`: Dumbbell Plot
* `diverging_bar_chart`: Diverging Bar Chart
* `small_multiples_line_graphs`: Small Multiples of Line Graphs
* `small_multiples_of_pie_charts`: Small Multiples of Pie Charts
* `alluvial_diagram`: Alluvial / Sankey Diagram
* `treemap`: Treemap
* `voronoi_treemap`: Voronoi Treemap
### 6. Other Charts
* `radar`: Radar Chart
* `funnel_chart`: Funnel Chart
* `pyramid_chart`: Pyramid Chart
* `gauge_chart`: Gauge Chart
---
Consider visual layout, structure, geometry, and color grouping in your assessment. You may return multiple guesses per category, but always prioritize ranking by **visual similarity**.