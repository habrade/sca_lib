<?xml version="1.0" encoding="UTF-8"?>
<databrowser>
  <title>Humidity</title>
  <show_toolbar>true</show_toolbar>
  <grid>true</grid>
  <update_period>1.0</update_period>
  <scroll_step>1</scroll_step>
  <scroll>true</scroll>
  <start>-30 minutes</start>
  <end>now</end>
  <archive_rescale>STAGGER</archive_rescale>
  <foreground>
    <red>0</red>
    <green>0</green>
    <blue>0</blue>
  </foreground>
  <background>
    <red>255</red>
    <green>255</green>
    <blue>255</blue>
  </background>
  <title_font>
  </title_font>
  <label_font>
  </label_font>
  <scale_font>
  </scale_font>
  <legend_font>
  </legend_font>
  <axes>
    <axis>
      <visible>true</visible>
      <name>Value 1</name>
      <use_axis_name>false</use_axis_name>
      <use_trace_names>false</use_trace_names>
      <right>false</right>
      <color>
        <red>0</red>
        <green>0</green>
        <blue>0</blue>
      </color>
      <min>1.8141032021604928</min>
      <max>7.6011402391975285</max>
      <grid>false</grid>
      <autoscale>true</autoscale>
      <log_scale>false</log_scale>
    </axis>
  </axes>
  <annotations>
  </annotations>
  <pvlist>
    <pv>
      <display_name>$(P):BME280:Humidity</display_name>
      <visible>true</visible>
      <name>$(P):BME280:Humidity</name>
      <axis>0</axis>
      <color>
        <red>128</red>
        <green>77</green>
        <blue>128</blue>
      </color>
      <trace_type>AREA</trace_type>
      <linewidth>2</linewidth>
      <line_style>SOLID</line_style>
      <point_type>NONE</point_type>
      <point_size>2</point_size>
      <waveform_index>0</waveform_index>
      <period>0.0</period>
      <ring_size>5000</ring_size>
      <request>OPTIMIZED</request>
      <archive>
        <name>RDB</name>
        <url>jdbc:mysql://localhost/archive</url>
      </archive>
      <archive>
        <name>xnds://localhost/archive/cgi/ArchiveDataServer.cgi</name>
        <url>xnds://localhost/archive/cgi/ArchiveDataServer.cgi</url>
      </archive>
    </pv>
  </pvlist>
</databrowser>
