// Source header
#include "PreamblePragmaHandler.hpp"

// Standard library
#include <chrono>
#include <thread>

// Clang
#include <clang/Basic/Diagnostic.h>
#include <clang/Lex/PPCallbacks.h>
#include <clang/Basic/Module.h>

// Mirror
#include "Globals.hpp"
#include "Utility.hpp"
#include "IncludeHandler.hpp"

namespace QED { namespace Pragmatic
{
	void PreamblePragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken) 
	{
		preProcessor.addPPCallbacks(std::make_unique<IncludeCallbacks>(preProcessor));
	}
}} // namesapce QED::Pragmatic