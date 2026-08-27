@echo off
:: ============================================================================
:: Adaptive Underworld Recon Array (A.U.R.A.)
:: Copyright (C) 2026 JeffTheNerdDev96
::
:: This program is free software: you can redistribute it and/or modify
:: it under the terms of the GNU Affero General Public License as published by
:: the Free Software Foundation, either version 3 of the License, or
:: (at your option) any later version.
::
:: This program is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
:: GNU Affero General Public License for more details.
::
:: You should have received a copy of the GNU Affero General Public License
:: along with this program.  If not, see <https://www.gnu.org/licenses/>.
:: ============================================================================
cd /d "%~dp0"
set PYTHONUTF8=1
if exist "requirements\venv\Scripts\python.exe" (
  "requirements\venv\Scripts\python.exe" -c "from bootstrap import configure_qt_paths; configure_qt_paths()" && "requirements\venv\Scripts\python.exe" app.py
) else if exist "runtime\python.exe" (
  "runtime\python.exe" -c "from bootstrap import configure_qt_paths; configure_qt_paths()" && "runtime\python.exe" app.py
) else (
  echo Python environment not found.
  pause
  exit /b 1
)
pause
