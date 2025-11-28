"""
UI模块 - 负责Streamlit界面的渲染和交互
"""

import streamlit as st
import os
import time
import shutil
from typing import TYPE_CHECKING
from i18n import get_i18n, t
import inspect

if TYPE_CHECKING:
    from main import MolecularWeightAnalyzer, GPCAnalyzer, DSCAnalyzer

# 全局变量
i18n = get_i18n()


def render_dsc_ui(default_dir: str, AnalyzerClass: type) -> None:
    """渲染DSC分析UI标签页
    
    Args:
        default_dir: 默认数据目录
        AnalyzerClass: DSC分析器类
    """
    
    datapath_dsc = st.text_input(t("data_folder"), value=default_dir, placeholder=t("data_folder"), key="datapath_dsc")
    if not os.path.isdir(datapath_dsc):
        st.warning(t("invalid_path"))
        
    # 参数选择
    saveSegMode_col, drawSegMode_col, drawCycle_col, displayPic_col, saveCyclePic_col, peaksUpward_col, testMode_col = st.columns(spec=7)
    saveSegMode = saveSegMode_col.checkbox(t("save_segment_data"), value=True)
    drawSegMode = drawSegMode_col.checkbox(t("draw_segment_data"), value=True)
    drawCycle = drawCycle_col.checkbox(t("draw_cycle"), value=saveSegMode, disabled=not saveSegMode)
    displayPic = displayPic_col.checkbox(t("display_cycle"), value=saveSegMode and drawCycle, disabled=not (saveSegMode and drawCycle))
    saveCyclePic = saveCyclePic_col.checkbox(t("save_cycle"), value=saveSegMode and drawCycle, disabled=not (saveSegMode and drawCycle))
    peaksUpward = peaksUpward_col.checkbox(t("peaks_upward"), value=False)
    centerPeak = peaksUpward_col.checkbox(t("center_peak"), value=False)
    testMode = testMode_col.checkbox(t("test_mode"), value=False, disabled=True)

    leftSide_col, rightSide_col = st.columns(spec=2)
    leftSide = leftSide_col.slider(label=t("left_boundary"), min_value=0.0, max_value=3.0, value=0.5, step=0.1)
    rightSide = rightSide_col.slider(label=t("right_boundary"), min_value=0.0, max_value=3.0, value=0.5, step=0.1)
    
    avilible = any([saveSegMode, drawSegMode, drawCycle, saveCyclePic, displayPic])

    if not avilible:
        st.warning(t("select_at_least_one"))

    # 初始化进度条和信息栏
    progressBar_dsc = st.empty()
    infoBar_dsc = st.empty()
    
    def progress_callback(progress: float, text: str):
        progressBar_dsc.progress(progress, text)
        
    def info_callback(text: str):
        infoBar_dsc.text(text)

    dsc = AnalyzerClass(datadir=datapath_dsc, test_mode=testMode, save_seg_mode=saveSegMode, 
                      draw_seg_mode=drawSegMode, draw_cycle=drawCycle, display_pic=displayPic, 
                      save_cycle_pic=saveCyclePic, peaks_upward=peaksUpward, center_peak=centerPeak,
                      left_length=leftSide, right_length=rightSide,
                      progress_callback=progress_callback, info_callback=info_callback)
    
    # 画图设置
    render_dsc_settings(dsc)
    
    run_col_dsc, infoBar_col_dsc, openDir_dsc_col, *_ = st.columns(spec=11)
                      
    if run_col_dsc.button(t("run"), key="run_col_dsc", disabled=not avilible):
        task_start_time = time.time()
        infoBar_dsc = infoBar_col_dsc.empty()
        result_dsc = dsc.run()
        infoBar_dsc.text(t("complete", time.time() - task_start_time))

    if os.path.isdir(datapath_dsc):
        if openDir_dsc_col.button(t("open_folder"), key="openDir_dsc_col"):
            dsc.open_folder(dsc.rootdir)


def render_dsc_settings(dsc: 'DSCAnalyzer') -> None:
    """渲染DSC分析器的设置界面
    
    Args:
        dsc: DSC分析器实例
    """
    picSet = st.expander(t("plot_settings"))
   
    with picSet:
        # 第一行：绘图参数(前3个) + 配置管理(选择/删除)
        curveColor_col, transparentBack_col, lineWidth_col, _, settingList_col, deleteSetting_col = st.columns(6)
        
        dsc.curve_color = curveColor_col.color_picker(t("curve_color"), value=dsc.curve_color, key="dsc_curveColor_col")
        dsc.transparent_back = transparentBack_col.checkbox(t("transparent_background"), value=dsc.transparent_back, key="dsc_transparentBack_col")
        dsc.line_width = lineWidth_col.slider(t("line_width"), key="dsc_lineWidth_col", min_value=0.2, max_value=3.0, step=0.1, value=dsc.line_width)
        
        dsc.setting_name = settingList_col.selectbox(t("settings_list"), dsc.setting_list(), key="dsc_settingList_col")
        deleteSetting_col.button(t("delete_setting"), key="dsc_deleteSetting_col", on_click=dsc.delete_setting, args=[dsc.setting_name])
        
        # 第二行：绘图参数(后3个) + 配置管理(切换/保存)
        axisWidth_col, titleFontSize_col, axisFontSize_col, switchSetting_col, settingname_col, saveSetting_col = st.columns(6)
        
        dsc.axis_width = axisWidth_col.slider(t("axis_width"), key="dsc_axisWidth_col", min_value=0.5, max_value=3.0, step=0.1, value=dsc.axis_width)
        dsc.title_font_size = titleFontSize_col.slider(t("title_font_size"), key="dsc_titleFontSize_col", min_value=10, max_value=28, step=1, value=dsc.title_font_size)
        dsc.axis_font_size = axisFontSize_col.slider(t("axis_font_size"), key="dsc_axisFontSize_col", min_value=8, max_value=24, step=1, value=dsc.axis_font_size)
        
        switchSetting_col.button(t("switch_setting"), key="dsc_switchSetting_col", on_click=dsc.change_setting, args=[dsc.setting_name])
        newsettingname = settingname_col.text_input(t("setting_name"), key="dsc_saveRegion_col", value=dsc.setting_name)
        saveSetting_col.button(t("save_setting"), key="dsc_saveSetting_col", on_click=dsc.save_setting, args=[newsettingname], disabled=(dsc.setting_name == newsettingname))


def render_mw_settings(mw: 'MolecularWeightAnalyzer') -> None:
    """渲染分子量分析器的设置界面
    
    Args:
        mw: 分子量分析器实例
    """
    picSet = st.expander(t("plot_settings"))
   
    with picSet:
        barColor_col, MwColor_col, transparentBack_col, drawBar_col, drawMw_col, drawTable_col, settingList_col, deleteSetting_col, *_ = st.columns(spec=8)
        barWidth_col, lineWidth_col, axisWidth_col, titleFontSize_col, axisFontSize_col, switchSetting_col, settingname_col, saveSetting_col, *_ = st.columns(spec=8)
        
        # 第一行：颜色和绘图选项
        mw.bar_color = barColor_col.color_picker(t("bar_color"), value=mw.bar_color, key="barColor_col")
        mw.mw_color = MwColor_col.color_picker(t("mw_color"), value=mw.mw_color, key="MwColor_col")
        mw.transparent_back = transparentBack_col.checkbox(t("transparent_background"), value=mw.transparent_back, key="transparentBack_col")
        mw.draw_bar = drawBar_col.checkbox(t("draw_bar"), value=mw.draw_bar, key="drawBar_col")
        mw.draw_mw = drawMw_col.checkbox(t("draw_mw"), value=mw.draw_mw, key="drawMw_col")
        mw.draw_table = drawTable_col.checkbox(t("draw_table"), value=mw.draw_table, key="drawTable_col")
        mw.setting_name = settingList_col.selectbox(t("settings_list"), mw.setting_list(), key="settingList_col")
        deleteSetting_col.button(t("delete_setting"), key="deleteSetting_col", on_click=mw.delete_setting, args=[mw.setting_name])
        
        # 第二行：尺寸和字体调整
        mw.bar_width = barWidth_col.slider(t("bar_width"), key="barWidth_col", min_value=0.2, max_value=2.0, step=0.1, value=mw.bar_width)
        mw.line_width = lineWidth_col.slider(t("line_width"), key="lineWidth_col", min_value=0.2, max_value=2.0, step=0.1, value=mw.line_width)
        mw.axis_width = axisWidth_col.slider(t("axis_width"), key="axisWidth_col", min_value=0.5, max_value=2.0, step=0.1, value=mw.axis_width)
        mw.title_font_size = titleFontSize_col.slider(t("title_font_size"), key="titleFontSize_col", min_value=14, max_value=28, step=1, value=mw.title_font_size)
        mw.axis_font_size = axisFontSize_col.slider(t("axis_font_size"), key="axisFontSize_col", min_value=10, max_value=18, step=1, value=mw.axis_font_size)
        switchSetting_col.button(t("switch_setting"), key="switchSetting_col", on_click=mw.change_setting, args=[mw.setting_name])
        newsettingname = settingname_col.text_input(t("setting_name"), key="saveRegion_col", value=mw.setting_name)
        saveSetting_col.button(t("save_setting"), key="saveSetting_col", on_click=mw.save_setting, args=[newsettingname], disabled=(mw.setting_name == newsettingname))


def render_mw_region_settings(mw: 'MolecularWeightAnalyzer') -> None:
    """渲染分子量区域设置界面
    
    Args:
        mw: 分子量分析器实例
    """
    rangeSet = st.expander(t("region_settings"))

    with rangeSet:
        selectedRegion = st.multiselect(t("split_position"), mw.segmentpos, default=mw.selectedpos)
        selectedRegion.sort()
        mw.selectedpos = selectedRegion
        
        new_region_col, addRegion_col, *_ = st.columns(spec=6)
        new_region = new_region_col.number_input(t("new_split_position"), min_value=0, max_value=1000000000)
        addRegion_col.button(t("add_region"), key="addRegion_col", on_click=mw.add_region, args=[new_region])
        mw.selected_file = st.multiselect(t("file_list"), mw.read_file_list(), default=mw.read_file_list())


def render_mw_ui(default_dir: str, AnalyzerClass: type) -> None:
    """渲染分子量分析UI标签页
    
    Args:
        default_dir: 默认数据目录
        AnalyzerClass: 分子量分析器类
    """
    
    datapath_mw = st.text_input(t("data_folder"), value=default_dir, max_chars=100, key="datapath_mw")
    if not os.path.isdir(datapath_mw):
        st.warning(t("invalid_path"))

    savePic_mw_col, displayPic_mw_col, *_ = st.columns(spec=8)
    savePic_mw = savePic_mw_col.checkbox(t("save_image"), value=True, key="savePic_mw_col")
    displayPic_mw = displayPic_mw_col.checkbox(t("display_image"), value=False, key="displayPic_mw_col")
    
    st.empty()  # output_filename_mw_col
    st.empty()  # fileSelect_mw_col
    
    # 初始化进度条
    progressBar_mw = st.empty()
    
    # 定义进度回调函数
    def progress_callback(progress: float, text: str):
        progressBar_mw.progress(progress, text)
                
    mw = AnalyzerClass(datapath_mw, save_picture=savePic_mw, display_picture=displayPic_mw, 
                                  test_mode=False, progress_callback=progress_callback)
    
    # 画图设置
    render_mw_settings(mw)
    
    # 区域设置
    render_mw_region_settings(mw)
    
    # 运行控制
    run_mw_col, openDir_mw_col, infoBar_mw_col, *_ = st.columns(spec=8)
    
    overlayFile_mw = True
    if mw.check_dir():
        overlayFile_mw = st.checkbox(t("confirm_overwrite"), key="overlayFile_mw_col")
        if not overlayFile_mw:
            st.warning(t("file_exists_warning"))

    if run_mw_col.button(t("run"), key="run_mw_col_mw", disabled=not overlayFile_mw):
        task_start_time = time.time()
        infoBar_mw = infoBar_mw_col.empty()
        result_mw = mw.run()
        infoBar_mw.text(t("complete", time.time() - task_start_time))

    if os.path.isdir(datapath_mw):
        if openDir_mw_col.button(t("open_folder"), key="openDir_mw_col_mw"):
            mw.open_folder(mw.output_dir)


def render_gpc_ui(default_dir: str, AnalyzerClass: type) -> None:
    """渲染GPC分析UI标签页
    
    Args:
        default_dir: 默认数据目录
        AnalyzerClass: GPC分析器类
    """
    
    datapath_gpc = st.text_input(t("data_folder"), value=default_dir, max_chars=100, key="datapath_gpc")
    if not os.path.isdir(datapath_gpc):
        st.warning(t("invalid_path"))

    save_file_col, save_picture_col, display_mode_col, save_figure_file_gpc_col, selected_gpc_col, draw_mw_col, *_ = st.columns(spec=8)
    save_file = save_file_col.checkbox(t("save_sample_info"), value=True)
    save_picture = save_picture_col.checkbox(t("save_image"), value=True)
    display_mode = display_mode_col.checkbox(t("display_image"), value=True)
    save_figure_file_gpc = save_figure_file_gpc_col.checkbox(t("save_plot_data"), value=False)
    selected = selected_gpc_col.checkbox(t("select_partial_files"))

    output_filename = st.text_input(t("output_filename"), value=time.strftime("%Y%m%d", time.localtime()), max_chars=100, key="output_filename", disabled=not (save_file or save_picture))
    overlayFile_col = st.empty()
    fileSelect_col = st.empty()
    run_gpc_col, openDir_gpc_col, infoBar_gpc_col, *_ = st.columns(spec=8)
    
    # 初始化进度条和信息栏
    progressBar_gpc = st.empty()
    infoBar_gpc = st.empty()
    
    # 定义回调函数
    def progress_callback(progress: float, text: str):
        progressBar_gpc.progress(progress, text)
    
    def info_callback(text: str):
        infoBar_gpc.text(text)
    
    gpc = AnalyzerClass(datapath_gpc, output_filename, save_file, save_picture, display_mode, 
                      save_figure_file_gpc, test_mode=False, 
                      progress_callback=progress_callback, info_callback=info_callback)

    if selected:
        gpc.selected_file = fileSelect_col.multiselect(t("file_list"), gpc.read_file_list())
        
    overlayFile = True
    if gpc.check_dir():
        overlayFile = overlayFile_col.checkbox(t("confirm_overwrite"))
        if not overlayFile:
            st.warning(t("file_exists_warning"))  

    if run_gpc_col.button(t("run"), key="run_gpc_col", disabled=not overlayFile):
        task_start_time = time.time()
        infoBar_gpc = infoBar_gpc_col.empty()
        result_gpc = gpc.run()
        infoBar_gpc.text(t("complete", time.time() - task_start_time))

    if os.path.isdir(datapath_gpc):
        if openDir_gpc_col.button(t("open_folder"), key="openDir_gpc_col"):
            gpc.open_folder(gpc.output_dir)


def render_other_ui(default_dir: str) -> None:
    """渲染其他功能UI标签页
    
    Args:
        default_dir: 默认数据目录
    """
    datapath_other = st.text_input(t("data_folder"), value=default_dir, max_chars=100, key="datapath_other")
    if os.path.isdir(datapath_other):
        clear_confirm = st.checkbox(t("clean_folder"), value=False)
        if st.button(t("run_clean"), disabled=not clear_confirm):
            root_dir = os.getcwd()
            folders_to_clean = ["Mw_output", "GPC_output", "DSC_Cycle", "DSC_Pic"]
            
            for folder in folders_to_clean:
                folder_path = os.path.join(root_dir, folder)
                if os.path.exists(folder_path):
                    try:
                        # 清空文件夹内容但保留文件夹本身
                        for filename in os.listdir(folder_path):
                            file_path = os.path.join(folder_path, filename)
                            try:
                                if os.path.isfile(file_path) or os.path.islink(file_path):
                                    os.unlink(file_path)
                                elif os.path.isdir(file_path):
                                    shutil.rmtree(file_path)
                            except Exception as e:
                                st.error(f"Failed to delete {file_path}. Reason: {e}")
                    except Exception as e:
                        st.error(f"Error cleaning {folder_path}: {e}")
            
            st.success(t("clean_success"))
    else:
        st.warning(t("invalid_path"))


def render_sidebar() -> None:
    """渲染侧边栏"""
    with st.sidebar:
        # 语言选择
        st.subheader(t("language"))
        languages = i18n.get_available_languages()
        current_lang = i18n.get_language()
        
        # 创建语言选择框
        lang_options = list(languages.values())
        lang_codes = list(languages.keys())
        current_index = lang_codes.index(current_lang) if current_lang in lang_codes else 0
        
        selected_lang_name = st.selectbox(
            t("language"),
            options=lang_options,
            index=current_index,
            key="language_selector",
            label_visibility="collapsed"
        )
        
        # 如果语言改变，更新设置并重新加载
        selected_lang_code = lang_codes[lang_options.index(selected_lang_name)]
        if selected_lang_code != current_lang:
            i18n.set_language(selected_lang_code)
            st.rerun()
        
        # 帮助信息
        with st.expander(t("help"), expanded=True):
            st.markdown(t("contact_info"))


def render_app(DSCAnalyzerClass: type, GPCAnalyzerClass: type, MolecularWeightAnalyzerClass: type) -> None:
    """渲染完整的应用UI
    
    Args:
        DSCAnalyzerClass: DSC分析器类
        GPCAnalyzerClass: GPC分析器类
        MolecularWeightAnalyzerClass: 分子量分析器类
    """
    # 配置页面
    st.set_page_config(
        page_title=t("app_title"),
        page_icon='',
        layout='wide',
        initial_sidebar_state="collapsed"
    )
    
    # 默认数据目录
    default_dir = os.path.join(os.getcwd(), "datapath")
    
    # 创建标签页
    gpc_ui, Mw_ui, dsc_ui, other_ui = st.tabs([t("tab_gpc"), t("tab_mw"), t("tab_dsc"), t("tab_other")])
    
    with gpc_ui:
        render_gpc_ui(default_dir, GPCAnalyzerClass)
    
    with Mw_ui:
        render_mw_ui(default_dir, MolecularWeightAnalyzerClass)

    with dsc_ui:
        render_dsc_ui(default_dir, DSCAnalyzerClass)
    
    with other_ui:
        render_other_ui(default_dir)
    
    # 渲染侧边栏
    render_sidebar()


# 导出全局变量供main.py使用
__all__ = ['render_app', 'progressBar_mw', 'infoBar_mw', 'progressBar_gpc', 'infoBar_gpc', 'progressBar_dsc', 'infoBar_dsc']

# 这些变量需要在main.py中访问
progressBar_mw = None
infoBar_mw = None
progressBar_gpc = None
infoBar_gpc = None
progressBar_dsc = None
infoBar_dsc = None
