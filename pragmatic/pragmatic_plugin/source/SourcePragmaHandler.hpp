#pragma once

// Standard library
#include <vector>	// vector
#include <string>	// string

// Clang
#include <clang/Lex/Pragma.h>			// PragmaHandler
#include <clang/Lex/Preprocessor.h>		// PragmaHandlerRegistry

namespace QED { namespace Pragmatic
{
	class SourcePragmaHandler : public clang::PragmaHandler
	{
		public: // Constructor
		SourcePragmaHandler() : clang::PragmaHandler("source") { }

		public: // Clang functions
		void HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &sourceToken);

		private:
		void AddSourceToJSON(std::vector<std::string>& tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation location);
	};
}} // namesapce QED::Pragmatic