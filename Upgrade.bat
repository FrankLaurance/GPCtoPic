@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========================================
:: PolyAnalyzer 版本升级工具
:: 自动从旧版本迁移用户数据
:: ========================================

title PolyAnalyzer 版本升级工具

color 0A
echo.
echo ========================================
echo   PolyAnalyzer 版本升级工具
echo ========================================
echo.

:: 获取当前文件夹名称和版本号
for %%I in ("%~dp0.") do set "CURRENT_FOLDER=%%~nxI"
echo 当前版本文件夹: %CURRENT_FOLDER%

:: 从文件夹名称中提取版本号 (格式: PolyAnalyzer_Windows_Portable_vX.X.X)
for /f "tokens=2 delims=v" %%V in ("%CURRENT_FOLDER%") do set "CURRENT_VERSION=%%V"
if "%CURRENT_VERSION%"=="" (
    echo [错误] 无法识别当前版本号
    echo 请确保文件夹名称格式为: PolyAnalyzer_Windows_Portable_vX.X.X
    pause
    exit /b 1
)

echo 当前版本号: v%CURRENT_VERSION%
echo.

:: 列出父目录中的其他 PolyAnalyzer 文件夹
echo 正在扫描其他版本...
echo.

set "PARENT_DIR=%~dp0.."
set "FOUND_OLD_VERSION="
set /a FOLDER_COUNT=0

:: 扫描所有 PolyAnalyzer 文件夹
for /d %%D in ("%PARENT_DIR%\PolyAnalyzer_Windows_Portable_v*") do (
    set "FOLDER_NAME=%%~nxD"
    if not "!FOLDER_NAME!"=="%CURRENT_FOLDER%" (
        set /a FOLDER_COUNT+=1
        echo [!FOLDER_COUNT!] 发现旧版本: !FOLDER_NAME!
        
        :: 提取旧版本号
        for /f "tokens=2 delims=v" %%V in ("!FOLDER_NAME!") do set "OLD_VERSION_!FOLDER_COUNT!=%%V"
        set "OLD_FOLDER_!FOLDER_COUNT!=%%D"
        set "OLD_NAME_!FOLDER_COUNT!=!FOLDER_NAME!"
    )
)

if %FOLDER_COUNT%==0 (
    echo.
    echo [提示] 未发现其他版本
    echo 这可能是首次安装，无需升级
    pause
    exit /b 0
)

echo.
echo ========================================
echo 发现 %FOLDER_COUNT% 个旧版本
echo ========================================
echo.

:: 显示所有旧版本并让用户选择
if %FOLDER_COUNT%==1 (
    echo 将从以下版本迁移数据:
    echo   v!OLD_VERSION_1! - !OLD_NAME_1!
    echo.
    set /p "CONFIRM=是否继续? (Y/N): "
    if /i not "!CONFIRM!"=="Y" (
        echo 升级已取消
        pause
        exit /b 0
    )
    set "SELECTED=1"
) else (
    echo 请选择要迁移数据的版本:
    for /l %%i in (1,1,%FOLDER_COUNT%) do (
        echo   [%%i] v!OLD_VERSION_%%i! - !OLD_NAME_%%i!
    )
    echo   [0] 取消升级
    echo.
    set /p "SELECTED=请输入编号 (0-%FOLDER_COUNT%): "
    
    if "!SELECTED!"=="0" (
        echo 升级已取消
        pause
        exit /b 0
    )
    
    if !SELECTED! LSS 1 (
        echo [错误] 无效的选择
        pause
        exit /b 1
    )
    if !SELECTED! GTR %FOLDER_COUNT% (
        echo [错误] 无效的选择
        pause
        exit /b 1
    )
)

:: 设置源文件夹和目标文件夹
set "SOURCE_FOLDER=!OLD_FOLDER_%SELECTED%!"
set "TARGET_FOLDER=%~dp0"
set "OLD_VERSION=!OLD_VERSION_%SELECTED%!"
set "OLD_NAME=!OLD_NAME_%SELECTED%!"

echo.
echo ========================================
echo 开始升级
echo ========================================
echo 源版本: v%OLD_VERSION%
echo 目标版本: v%CURRENT_VERSION%
echo.

:: 定义需要迁移的用户数据文件夹/文件
set "USER_DIRS=GPC_output Mw_output DSC_Pic DSC_Cycle logs setting datapath"

:: 迁移用户数据
echo [1/3] 正在迁移用户数据...
echo.

for %%D in (%USER_DIRS%) do (
    if exist "%SOURCE_FOLDER%\%%D\" (
        echo   - 迁移: %%D\
        
        :: 如果目标文件夹存在，先备份
        if exist "%TARGET_FOLDER%%%D\" (
            echo     (目标已存在，创建备份)
            if exist "%TARGET_FOLDER%%%D.bak\" (
                rd /s /q "%TARGET_FOLDER%%%D.bak" 2>nul
            )
            move "%TARGET_FOLDER%%%D" "%TARGET_FOLDER%%%D.bak" >nul 2>&1
        )
        
        :: 复制文件夹
        xcopy "%SOURCE_FOLDER%\%%D" "%TARGET_FOLDER%%%D\" /E /I /Y /Q >nul 2>&1
        if !errorlevel! equ 0 (
            echo     [成功]
        ) else (
            echo     [警告] 复制失败，可能部分文件未复制
        )
    ) else (
        echo   - 跳过: %%D\ (源文件夹不存在)
    )
)

echo.
echo [2/3] 数据迁移完成！
echo.

:: 询问是否删除旧版本
echo [3/3] 清理旧版本
echo.
set /p "DELETE_OLD=是否删除旧版本文件夹? (Y/N): "

if /i "!DELETE_OLD!"=="Y" (
    echo.
    echo 正在删除旧版本: %OLD_NAME%
    echo 请稍候...
    
    :: 删除旧版本文件夹
    rd /s /q "%SOURCE_FOLDER%" 2>nul
    
    if !errorlevel! equ 0 (
        echo [成功] 旧版本已删除
    ) else (
        echo [警告] 删除失败，请手动删除:
        echo   %SOURCE_FOLDER%
    )
) else (
    echo.
    echo [提示] 保留旧版本文件夹
    echo 如需手动删除，路径为:
    echo   %SOURCE_FOLDER%
)

echo.
echo ========================================
echo 升级完成！
echo ========================================
echo.
echo 迁移的数据:
for %%D in (%USER_DIRS%) do (
    if exist "%TARGET_FOLDER%%%D\" (
        echo   ✓ %%D
    )
)
echo.
echo 现在可以启动新版本的 PolyAnalyzer
echo.

color 0E
echo 按任意键退出...
pause >nul
exit /b 0
