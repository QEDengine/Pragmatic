#pragma once

// Standard library
#include <string>
#include <vector>

// Clang
#include "clang/Basic/Diagnostic.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Lex/Preprocessor.h"
#include "clang/Basic/LangStandard.h"

// Pragmatic
#include "PragmaHandler.hpp"

namespace QED { namespace Pragmatic
{
	class StandardPragma : public PragmaHandler
	{
		public:
		StandardPragma();

		private:
		std::string standard = "";

		protected:
		virtual bool CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation) override;
		virtual std::string Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics) override;
	};

}} // namespace QED::Pragmatic